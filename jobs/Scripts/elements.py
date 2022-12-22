import os
import platform


class ElementLocation:
    def __init__(self, location, element_name):
        self.location = location
        self.element_name = element_name

    def build_path(self):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Elements", self.location, self.element_name) + ".png")


class USDViewLocation(ElementLocation):
    def __init__(self, element_name):
        if platform.system() == "Windows":
            super().__init__("Windows", element_name)
        else:
            super().__init__("Ubuntu", element_name)


class USDViewElements:
    CAMERA = USDViewLocation("camera")
    ENABLE_COLOR_ALPHA = USDViewLocation("enable_color_alpha")
    ENABLE_GAMMA = USDViewLocation("enable_gamma")
    ENABLE_TONE_MAPPING = USDViewLocation("enable_tone_mapping")
    HYBRID_PRO = USDViewLocation("hybrid_pro")
    HYDRA_SETTINGS = USDViewLocation("hydra_settings")
    MORE = USDViewLocation("more")
    NORTHSTAR = USDViewLocation("northstar")
    RENDER_QUALITY = USDViewLocation("render_quality")
    RENDERER = USDViewLocation("renderer")
    RPR = USDViewLocation("rpr")
    SAVE_VIEWER_IMAGE = USDViewLocation("save_viewer_image")
    UV_THRESHOLD = USDViewLocation("uv_threshold")
