import os
import logging
import pyautogui
import time
import win32gui
import win32con
import json
from pyautogui import typewrite, press
import psutil
from psutil import Popen, NoSuchProcess
from subprocess import PIPE
import sys
import traceback
from PIL import Image
from elements import USDViewElements

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
import local_config


pyautogui.FAILSAFE = False


# Logger for current test case
case_logger = None
# Application process
process = None


def close_process(process):
    try:
        child_processes = process.children()
        case_logger.info(f"Child processes: {child_processes}")
        for ch in child_processes:
            try:
                ch.kill()
            except NoSuchProcess:
                case_logger.info(f"Process is killed: {ch}")

        try:
            process.kill()
        except NoSuchProcess:
            case_logger.info(f"Process is killed: {process}")

        time.sleep(0.5)

        for ch in child_processes:
            try:
                status = ch.status()
                case_logger.error(f"Process is alive: {ch}. Name: {ch.name()}. Status: {status}")
            except NoSuchProcess:
                case_logger.info(f"Process is killed: {ch}")

        try:
            status = process.status()
            case_logger.error(f"Process is alive: {process}. Name: {process.name()}. Status: {status}")
        except NoSuchProcess:
            case_logger.info(f"Process is killed: {process}")
    except Exception as e:
        case_logger.error(f"Failed to close process: {str(e)}")
        case_logger.error(f"Traceback: {traceback.format_exc()}")


def open_tool(script_path, execution_script):
    global process

    with open(script_path, "w") as f:
        f.write(execution_script)

    process = psutil.Popen(script_path, stdout=PIPE, stderr=PIPE)

    time.sleep(3)

    window_hwnd = None

    for window in pyautogui.getAllWindows():
        if ".usd" in window.title:
            window_hwnd = window._hWnd
            break

    if not window_hwnd:
        raise Exception("Application window not found")

    pyautogui.hotkey("win", "m")
    time.sleep(1)
    win32gui.ShowWindow(window_hwnd, win32con.SW_MAXIMIZE)
    time.sleep(1)


def set_render_quality(engine):
    locate_and_click(USDViewElements.RPR.build_path())
    time.sleep(0.5)
    locate_and_click(USDViewElements.RENDER_QUALITY.build_path())
    time.sleep(0.5)

    if engine == "Northstar":
        locate_and_click(USDViewElements.NORTHSTAR.build_path())
    elif engine == "HybridPro":
        locate_and_click(USDViewElements.HYBRID_PRO.build_path())
    else:
        raise ValueError(f"Unexpected engine '{engine}'")


def post_action():
    try:
        close_process(process)
    except Exception as e:
        case_logger.error(f"Failed to do post actions: {str(e)}")
        case_logger.error(f"Traceback: {traceback.format_exc()}")


def create_case_logger(case_name, log_path):
    formatter = logging.Formatter(fmt=u'[%(asctime)s] #%(levelname)-6s [F:%(filename)s L:%(lineno)d] >> %(message)s')

    file_handler = logging.FileHandler(filename=os.path.join(log_path, f"{case_name}.log"), mode='a')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger(f"{case_name}")
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    global case_logger
    case_logger = logger


def is_case_skipped(case, render_platform):
    if case['status'] == 'skipped':
        return True

    return sum([render_platform & set(x) == set(x) for x in case.get('skip_on', '')])


def save_image(image_path):
    locate_and_click(USDViewElements.CAMERA.build_path())
    time.sleep(0.5)
    locate_and_click(USDViewElements.SAVE_VIEWER_IMAGE.build_path())
    time.sleep(0.5)
    pyautogui.typewrite(image_path)
    pyautogui.press("enter")
    time.sleep(0.5)


def disable_bounding_boxes():
    locate_and_click(USDViewElements.DISPLAY.build_path())
    time.sleep(0.5)
    locate_and_click(USDViewElements.BOUNDING_BOX.build_path())
    time.sleep(0.5)

    try:
        locate_on_screen(USDViewElements.SHOW_BOUNDING_BOXES_OFF.build_path(), tries=1, confidence=0.99)
    except:
        locate_and_click(USDViewElements.SHOW_BOUNDING_BOXES_LABEL.build_path())
        time.sleep(0.5)


def disable_hud():
    locate_and_click(USDViewElements.DISPLAY.build_path())
    time.sleep(0.5)
    locate_and_click(USDViewElements.HEADS_UP_DISPLAY.build_path())
    time.sleep(0.5)

    try:
        locate_on_screen(USDViewElements.SHOW_HUD_OFF.build_path(), tries=1, confidence=0.99)
    except:
        locate_and_click(USDViewElements.SHOW_HUD_LABEL.build_path())
        time.sleep(0.5)


def set_camera_options():
    locate_and_click(USDViewElements.LIGHTS.build_path())
    time.sleep(0.5)

    try:
        locate_on_screen(USDViewElements.ENABLE_SCENE_LIGHTS_ON.build_path(), tries=1, confidence=0.99)
    except:
        locate_and_click(USDViewElements.ENABLE_SCENE_LIGHTS_LABEL.build_path())
        time.sleep(0.5)
        locate_and_click(USDViewElements.LIGHTS.build_path())
        time.sleep(0.5)

    try:
        locate_on_screen(USDViewElements.ENABLE_DEFAULT_CAMERA_LIGHT_OFF.build_path(), tries=1, confidence=0.99)
    except:
        locate_and_click(USDViewElements.ENABLE_DEFAULT_CAMERA_LIGHT_LABEL.build_path(), confidence=0.97)
        time.sleep(0.5)
        locate_and_click(USDViewElements.LIGHTS.build_path())
        time.sleep(0.5)

    try:
        locate_on_screen(USDViewElements.ENABLE_DEFAULT_DOME_LIGHT_OFF.build_path(), tries=1, confidence=0.99)
    except:
        locate_and_click(USDViewElements.ENABLE_DEFAULT_DOME_LIGHT_LABEL.build_path(), confidence=0.97)
        time.sleep(0.5)

    locate_and_click(USDViewElements.LIGHTS.build_path())


def close_app_through_button():
    locate_and_click(USDViewElements.CLOSE_BUTTON.build_path())


def locate_on_screen(template, tries=3, confidence=0.9, **kwargs):
    coords = None
    if not "confidence" in kwargs:
        kwargs["confidence"] = confidence
    while not coords and tries > 0 and kwargs["confidence"] > 0:
        case_logger.info("Trying to find {} on screen, confidence = {}".format(template, kwargs["confidence"]))
        with Image.open(template) as img:
            coords = pyautogui.locateOnScreen(img, **kwargs)
        tries -= 1
        kwargs["confidence"] -= 0.07
    if not coords:
        raise Exception("No such element on screen")
    return (coords[0], coords[1], coords[2], coords[3])


def move_to(x, y):
    case_logger.info("Move to x = {}, y = {}".format(x, y))
    pyautogui.moveTo(x, y)


def click_on_element(coords, x_offset=0, y_offset=0):
    x = coords[0] + coords[2] / 2 + x_offset
    y = coords[1] + coords[3] / 2 + y_offset
    pyautogui.moveTo(x, y)
    time.sleep(0.3)
    pyautogui.click()
    case_logger.info("Click at x = {}, y = {}".format(x, y))


def locate_and_click(template, tries=3, confidence=0.9, x_offset=0, y_offset=0, **kwargs):
    coords = locate_on_screen(template, tries=tries, confidence=confidence, **kwargs)
    click_on_element(coords, x_offset=x_offset, y_offset=y_offset)
