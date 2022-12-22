import os
import logging
import pyautogui
import time
import json
import psutil
from psutil import Popen, NoSuchProcess
import subprocess
from subprocess import PIPE
import sys
import traceback
from PIL import Image
import pyscreenshot
from datetime import datetime
from shutil import copyfile
import platform
from collections import OrderedDict
from elements import USDViewElements

if platform.system() == "Windows":
    import win32api
    import win32gui
    import win32con
    import win32process

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


def open_tool(script_path, execution_script, engine, case=None, is_first_opening=False):
    global process

    # copy baseline state.json of usdview with necessary settings
    state_file_location = os.path.join(os.path.expanduser("~"), ".usdview")
    state_file_name = "state.json"

    target_file_location = os.path.join(state_file_location, state_file_name)
    source_file_location = os.path.join(os.path.dirname(__file__), "state", state_file_name)

    if not os.path.exists(state_file_location):
        os.makedirs(state_file_location)

    if os.path.exists(target_file_location):
        os.remove(target_file_location)

    copyfile(source_file_location, target_file_location)

    if case:
        modify_state_file(case, target_file_location)

    with open(script_path, "w") as f:
        f.write(execution_script)

    if platform.system() == "Windows":
        pyautogui.hotkey("win", "m")
    else:
        pyautogui.hotkey("win", "d")
        os.system(f"chmod +x {script_path}")

    time.sleep(1)

    process = psutil.Popen(script_path, stdout=PIPE, stderr=PIPE, shell=True)

    time.sleep(3)

    window_found, window_hwnd = does_application_windows_exist()

    if not window_found:
        raise Exception("Application window not found")
    else:
        case_logger.info("Application window found")

    if platform.system() == "Windows":
        process_application_stucking(script_path)
        win32gui.ShowWindow(window_hwnd, win32con.SW_MAXIMIZE)
    else:
        # on Ubuntu it's required some time after application first start up
        if is_first_opening:
            time.sleep(20)
        pyautogui.hotkey("win", "up")

    time.sleep(0.5)
    # pause render
    if engine == "HybridPro":
        pyautogui.hotkey("ctrl", "p")
        time.sleep(0.2)


def process_application_stucking(script_path):
    # check that application doesn't got stuck
    try:
        locate_on_screen(USDViewElements.APPLICATION_GOT_STUCK.build_path(), tries=1, confidence=0.95)
        case_logger.error("Application got stuck. Restart it")
        post_action()

        process = psutil.Popen(script_path, stdout=PIPE, stderr=PIPE)

        time.sleep(3)

        window_found = does_application_windows_exist()

        if not window_found:
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


def modify_state_file(case, state_path):
    with open(state_path, "r") as json_file:
        state = json.load(json_file)

    if "render_mode" in case:
        state["1"]["model"]["renderMode"] = case["render_mode"]

    if "prim_view_width" in case:
        state["1"]["ui"]["primViewWidth"] = case["prim_view_width"]
    if "stage_view_width" in case:
        state["1"]["ui"]["stageViewWidth"] = case["stage_view_width"]

    with open(state_path, "w") as json_file:
        json.dump(state, json_file, indent=4)


def set_render_settings(case):
    PADDINGS = OrderedDict()
    PADDINGS["ambient_occlusion_radius"] = 0
    PADDINGS["antialiasing"] = 1
    PADDINGS["use_normal"] = 2
    PADDINGS["linewidth_normal"] = 3
    PADDINGS["normal_threshold"] = 4
    PADDINGS["use_primitive_id"] = 5
    PADDINGS["linewidth_primitive_id"] = 6
    PADDINGS["use_material_id"] = 7
    PADDINGS["linewidth_material_id"] = 8
    PADDINGS["use_uv"] = 9
    PADDINGS["linewidth_uv"] = 10
    PADDINGS["uv_threshold"] = 11
    PADDINGS["debug"] = 12
    PADDINGS["enable_ai_denoising"] = 13
    PADDINGS["denoise_min_iteration"] = 14
    PADDINGS["denoise_iteration_step"] = 15
    PADDINGS["max_samples"] = 16
    PADDINGS["min_samples"] = 17
    PADDINGS["noise_threshold"] = 18
    PADDINGS["max_ray_depth"] = 19
    PADDINGS["diffuse_ray_depth"] = 20
    PADDINGS["glossy_ray_depth"] = 21
    PADDINGS["refraction_ray_depth"] = 22
    PADDINGS["glossy_refraction_ray_depth"] = 23
    PADDINGS["shadow_ray_depth"] = 24
    PADDINGS["ray_cast_epsilon"] = 25
    PADDINGS["max_radiance"] = 26
    PADDINGS["pixel_filter_width"] = 27
    PADDINGS["interactive_max_ray_depth"] = 28
    PADDINGS["interactive_resolution_downscale"] = 29
    PADDINGS["downscale_resolution_when_interactive"] = 30
    PADDINGS["enable_gamma"] = 31
    PADDINGS["gamma"] = 32
    PADDINGS["enable_tone_mapping"] = 33
    PADDINGS["film_exposure_time"] = 34
    PADDINGS["film_sensitivity"] = 35
    PADDINGS["fstop"] = 36
    PADDINGS["tone_mapping_gamma"] = 37
    PADDINGS["enable_color_alpha"] = 38
    PADDINGS["enable_beauty_motion_blur"] = 39
    PADDINGS["opencolorio_rendering_color_space"] = 40
    PADDINGS["use_uniform_seed"] = 41
    PADDINGS["cryptomatte_add_preview_layer"] = 42

    CHECK_BOXES = ["debug", "enable_ai_denoising"]

    last_field = None

    if "render_settings" in case:
        locate_and_click(USDViewElements.RENDERER.build_path())
        time.sleep(0.5)
        locate_and_click(USDViewElements.HYDRA_SETTINGS.build_path())
        time.sleep(0.5)
        locate_and_click(USDViewElements.MORE.build_path())
        time.sleep(0.5)

        for key in PADDINGS.keys():
            if key in case["render_settings"]:
                if last_field is None:
                    padding = PADDINGS[key]
                else:
                    padding = PADDINGS[key] - PADDINGS[last_field]

                for i in range(padding):
                    pyautogui.press("tab")
                    time.sleep(0.1)

                if key in CHECK_BOXES:
                    pyautogui.press("space")
                else:
                    pyautogui.hotkey("ctrl", "a")
                    time.sleep(0.1)
                    pyautogui.typewrite(str(case["render_settings"][key]))

                last_field = key

        pyautogui.press("enter")


def set_hydra_settings(case):
    if "hydra_settings" in case:
        def open_hydra_settings():
            locate_and_click(USDViewElements.RENDERER.build_path())
            time.sleep(0.5)
            locate_and_click(USDViewElements.HYDRA_SETTINGS.build_path())
            time.sleep(0.5)

        if "enable_gamma" in case["hydra_settings"]:
            open_hydra_settings()
            locate_and_click(USDViewElements.ENABLE_GAMMA.build_path())
            time.sleep(0.5)

        if "enable_color_alpha" in case["hydra_settings"]:
            open_hydra_settings()
            locate_and_click(USDViewElements.ENABLE_COLOR_ALPHA.build_path())
            time.sleep(0.5)

        if "enable_tone_mapping" in case["hydra_settings"]:
            open_hydra_settings()
            locate_and_click(USDViewElements.ENABLE_TONE_MAPPING.build_path())
            time.sleep(0.5)


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


def does_application_windows_exist():
    if platform.system() == "Windows":
        for window in pyautogui.getAllWindows():
            if ".usd" in window.title:
                return True, window._hWnd
    else:
        process = subprocess.Popen("wmctrl -l", stdout=PIPE, shell=True)
        stdout, stderr = process.communicate()
        windows = [" ".join(x.split()[3::]) for x in stdout.decode("utf-8").strip().split("\n")]

        for window in windows:
            if "assets" in window and ".usda" in window:
                return True, None

    return False, None


def post_action():
    try:
        if platform.system() == "Windows":
            process = find_usdview_process()
            close_process(process)
        else:
            process = subprocess.Popen("pkill -f .usda", stdout=PIPE, shell=True)
    except Exception as e:
        case_logger.warning(f"Failed to do post actions: {str(e)}")
        case_logger.warning(f"Traceback: {traceback.format_exc()}")


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
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)
    pyautogui.typewrite(image_path)
    pyautogui.press("enter")
    time.sleep(0.5)

    if not os.path.exists(image_path):
        raise Exception("Saved image not found")


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


def detect_render_finishing(max_delay=60):
    PREVIOUS_SCREEN_PATH = "previous_screenshot.jpg"
    CURRENT_SCREEN_PATH = "current_screenshot.jpg"

    def make_viewport_screenshot(screen_path):
        if os.path.exists(screen_path):
            os.remove(screen_path)

        resolution_x, resolution_y = get_resolution()

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
        prediction = metrics.getPrediction(mark_failed_if_black=True, max_size=5)

        # Viewport doesn't changed
        if prediction == 0:
            break

        make_viewport_screenshot(PREVIOUS_SCREEN_PATH)


def run_in_new_windows(command):
    if platform.system() == "Windows":
        return f"start cmd.exe @cmd /k \"{command} & exit 0\""
    else:
        return f"xterm -e \"{command}\""


def get_resolution():
    if platform.system() == "Windows":
        return win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    else:
        process = subprocess.Popen("xdpyinfo | awk '/dimensions/{print $2}'", stdout=PIPE, shell=True)
        stdout, stderr = process.communicate()
        resolution_x, resolution_y = stdout.decode("utf-8").strip().split("x")
        return int(resolution_x), int(resolution_y)
