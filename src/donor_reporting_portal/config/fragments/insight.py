from ..settings import env

INSIGHT_URL = env.str("INSIGHT_URL", "http://invalid_vision_url")
INSIGHT_LOGGER_MODEL = "vision.VisionLog"
INSIGHT_SUB_KEY = env.str("INSIGHT_SUB_KEY", "invalid_vision_password")
