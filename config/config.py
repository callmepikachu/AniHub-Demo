# =============================================================================
# config/config.py - 配置文件
# =============================================================================

class Config:
    """配置类"""

    # DeepSeek API 配置
    DEEPSEEK_API_KEY = "your_deepseek_api_key_here"
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

    # Kling AI API 配置
    KLING_API_KEY = "your_kling_api_key_here"
    KLING_API_URL = "https://api.kling.ai/v1/videos/generate"

    # 默认视频参数
    DEFAULT_VIDEO_PARAMS = {
        "duration": 5,
        "style": "realistic",
        "resolution": "1920x1080",
        "fps": 30
    }

    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"