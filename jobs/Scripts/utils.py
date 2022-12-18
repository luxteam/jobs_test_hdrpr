import os
import logging
import pyautogui
import time
import win32api
import win32gui
import win32con
import win32process
import json
from pyautogui import typewrite, press
import psutil
from psutil import Popen, NoSuchProcess
from subprocess import PIPE
import sys
import traceback
from PIL import Image
import pyscreenshot
from datetime import datetime
from elements import USDViewElements

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
import local_config
from jobs_launcher.common.scripts.CompareMetrics import CompareMetrics


pyautogui.FAILSAFE = False


# Logger for current test case
case_logger = None


ENGINES_LIST = set(["HybridPro", "Northstar"])


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


def open_tool(script_path, execution_script, engine):
    global process

    with open(script_path, "w") as f:
        f.write(execution_script)

    pyautogui.hotkey("win", "m")
    time.sleep(1)

    process = psutil.Popen(script_path, stdout=PIPE, stderr=PIPE, shell=True)

    time.sleep(3)

    window_hwnd = None

    for window in pyautogui.getAllWindows():
        if ".usd" in window.title:
            window_hwnd = window._hWnd
            break

    if not window_hwnd:
        raise Exception("Application window not found")
    else:
        case_logger.info("Application window found")

    # check that application doesn't got stuck
    try:
        locate_on_screen(USDViewElements.APPLICATION_GOT_STUCK.build_path(), tries=1, confidence=0.95)
        case_logger.error("Application got stuck. Restart it")
        post_action()

        process = psutil.Popen(script_path, stdout=PIPE, stderr=PIPE)

        time.sleep(3)

        window_hwnd = None

        for window in pyautogui.getAllWindows():
            if ".usd" in window.title:
                window_hwnd = window._hWnd
                break

        if not window_hwnd:
            raise Exception("Application window not found")
        else:
            case_logger.info("Application window found")

        try:
            locate_on_screen(USDViewElements.APPLICATION_GOT_STUCK.build_path(), tries=1, confidence=0.95)
            raise RuntimeError("Application got stuck")
        except RuntimeError as e:
            raise e
        except:
            case_logger.info("Application is running normally")

    except RuntimeError as e:
        raise e
    except:
        case_logger.info("Application is running normally")

    win32gui.ShowWindow(window_hwnd, win32con.SW_MAXIMIZE)
    time.sleep(0.5)
    # pause render
    if engine == "HybridPro":
        pyautogui.hotkey("ctrl", "p")
        time.sleep(0.2)


def set_render_settings(case):
    PADDINGS = {
        "max_ray_depth": 0,
        "diffuse_ray_depth": 1,
        "glossy_ray_depth": 2,
        "refraction_ray_depth": 3,
        "glossy_refraction_ray_depth": 4,
        "shadow_ray_depth": 5,
        "ray_case_epsilon": 6,
        "max_radiance": 7
    }

    last_field = None

    if "render_settings" in case:
        locate_and_click(USDViewElements.RENDERER.build_path())
        time.sleep(0.5)
        locate_and_click(USDViewElements.HYDRA_SETTINGS.build_path())
        time.sleep(0.5)
        locate_and_click(USDViewElements.MORE.build_path())
        time.sleep(0.5)

        # find label of first supporting render setting
        coords = locate_on_screen(USDViewElements.MAX_RAY_DEPTH.build_path())
        click_on_element(coords, x_offset=400)
        time.sleep(0.1)

        for key in case["render_settings"].keys():
            if key not in PADDINGS:
                raise Exception(f"Unexpected render setting {key}")

            if last_field is None:
                padding = PADDINGS[key]
            else:
                padding = PADDINGS[key] - PADDINGS[last_field]

            for i in range(padding):
                pyautogui.press("tab")
                time.sleep(0.1)

            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.1)
            pyautogui.typewrite(case["render_settings"][key])

            last_field = key

        pyautogui.press("enter")


def set_render_quality(engine):
    locate_and_click(USDViewElements.RPR.build_path())
    time.sleep(0.5)

    try:
        locate_and_click(USDViewElements.RENDER_QUALITY.build_path())
    except:
        # if render settins wasn't found, try to click RPR tab again
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


def find_usdview_process():
    for window in pyautogui.getAllWindows():
        if ".usd" in window.title:
            pid = win32process.GetWindowThreadProcessId(window._hWnd)[1]

            for process in psutil.process_iter():
                if process.pid == pid:
                    return process

    return None


def post_action():
    try:
        process = find_usdview_process()
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


def is_case_skipped(case, render_platform, gpu, engine):
    if case["status"] == "skipped":
        return True

    if "skip_config" in case:
        for config in case["skip_config"]:
            """
            Along with skipping the engine, we can set a certain configuration that we also want to skip.
            ["Hybrid"] - Skips this case with the specified engine on all machines
            ["Hybrid", "HybridPro", "GeForce RTX 2070"] - Skips this case with the specified engines on machines with RTX 2070
            ["Hybrid", "HybridPro", "GeForce RTX 2070", "GeForce RTX 2080 Ti"] - *WRONG CONFIG* It will not work, because the configuration has two video cards
            ["GeForce RTX 2070"] - Skips this case with the specified GPU on all machines
            ["GeForce RTX 2070", "Linux"] - Skips all Linux machines with a given GPU.
            ["Hybrid", "GeForce RTX 2070"] - Skips all machines with a GeForce RTX 2070 card regardless of the OS.
            ["Hybrid", "Windows", "GeForce RTX 2070"] - Skips the case only on Windows machines with a GeForce RTX 2070 graphics card and Hybrid engine.
            """
            config = set(config)
            skip_conf_by_eng = {engine}.union(render_platform)
            if skip_conf_by_eng.issuperset(config):
                return True
            elif (config - skip_conf_by_eng).issubset(ENGINES_LIST) and engine in config:
                """
                If the difference between the sets is equal to some other engine, then the config is designed for different engines.
                """
                return True

    if engine == "HybridPro" and not ("RTX" in gpu or "AMD Radeon RX 6" in gpu):
        return True

    return False 


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


def detect_render_finishing(max_delay=45):
    PREVIOUS_SCREEN_PATH = "previous_screenshot.jpg"
    CURRENT_SCREEN_PATH = "current_screenshot.jpg"

    def make_viewport_screenshot(screen_path):
        if os.path.exists(screen_path):
            os.remove(screen_path)

        resolution_x = win32api.GetSystemMetrics(0)
        resolution_y = win32api.GetSystemMetrics(1)

        # Approximately position of viewport
        viewport_region = (int(resolution_x / 2), 180, resolution_x - 20, int(resolution_y / 2))
        screen = pyscreenshot.grab(bbox=viewport_region)
        screen = screen.convert("RGB")
        screen.save(screen_path)

    start_time = datetime.now()

    make_viewport_screenshot(PREVIOUS_SCREEN_PATH)

    while True:
        if (datetime.now() - start_time).total_seconds() > max_delay:
            raise RuntimeError("Break waiting of render finishing due to timeout")

        time.sleep(3)

        make_viewport_screenshot(CURRENT_SCREEN_PATH)

        metrics = CompareMetrics(PREVIOUS_SCREEN_PATH, CURRENT_SCREEN_PATH)
        prediction = metrics.getPrediction(mark_failed_if_black=True, max_size=20)

        # Viewport doesn't changed
        if prediction == 0:
            break

        make_viewport_screenshot(PREVIOUS_SCREEN_PATH)
