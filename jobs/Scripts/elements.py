import os


class ElementLocation:
    def __init__(self, location, element_name):
        self.location = location
        self.element_name = element_name

    def build_path(self):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Elements", self.location, self.element_name) + ".png")


class USDViewLocation(ElementLocation):
    def __init__(self, element_name):
        super().__init__("", element_name)


class USDViewElements:
    CAMERA = USDViewLocation("camera")
    CLOSE_BUTTON = USDViewLocation("close_button")
    ENABLE_DEFAULT_CAMERA_LIGHT_LABEL = USDViewLocation("enable_default_camera_light_label")
    ENABLE_DEFAULT_CAMERA_LIGHT_ON = USDViewLocation("enable_default_camera_light_on")
    ENABLE_DEFAULT_CAMERA_LIGHT_OFF = USDViewLocation("enable_default_camera_light_off")
    ENABLE_DEFAULT_DOME_LIGHT_LABEL = USDViewLocation("enable_default_dome_light_label")
    ENABLE_DEFAULT_DOME_LIGHT_ON = USDViewLocation("enable_default_dome_light_on")
    ENABLE_DEFAULT_DOME_LIGHT_OFF = USDViewLocation("enable_default_dome_light_off")
    ENABLE_SCENE_LIGHTS_LABEL = USDViewLocation("enable_scene_lights_label")
    ENABLE_SCENE_LIGHTS_ON = USDViewLocation("enable_scene_lights_on")
    ENABLE_SCENE_LIGHTS_OFF = USDViewLocation("enable_scene_lights_off")
    HYBRID_PRO = USDViewLocation("hybrid_pro")
    LIGHTS = USDViewLocation("lights")
    NORTHSTAR = USDViewLocation("northstar")
    RENDER_QUALITY = USDViewLocation("render_quality")
    RPR = USDViewLocation("rpr")
    SAVE_VIEWER_IMAGE = USDViewLocation("save_viewer_image")
