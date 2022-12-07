import argparse
import os
import traceback
from time import sleep
import utils


SCENE_NAME = "planet/planetMaterialX.usda"
CAMERA = "Camera"


def createArgsParser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--tool_path", required=True)
    parser.add_argument("--res_path", required=True)
    parser.add_argument('--engine', required=True)
    parser.add_argument('--python', required=True)

    return parser


if __name__ == "__main__":
    args = createArgsParser().parse_args()

    rc = 0

    try:
        utils.create_case_logger("sanity", ".")

        tool_path = os.path.abspath(args.tool_path)
        scene_path = os.path.join(args.res_path, SCENE_NAME)
        execution_script = f"{args.python} {tool_path} -r RPR --camera {CAMERA} {scene_path}"
        script_path = "sanity.bat"

        image_path = os.path.abspath("sanity.jpg")

        utils.open_tool(script_path, execution_script)

        sleep(5)

        utils.set_camera_options()

        utils.set_render_quality(args.engine)

        sleep(10)

        utils.save_image(image_path)

        # Camera setting will be saved only after closing through button
        utils.close_app_through_button()
        sleep(0.5)
    except Exception as e:
        print(f"Failed during script execution. Exception: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        rc = -1
    finally:
        utils.post_action()

    exit(rc)
