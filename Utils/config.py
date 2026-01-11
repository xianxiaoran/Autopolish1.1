import os
from pathlib import Path


class AppConfig:
    """
    应用程序全局配置
    """
    # 基础信息
    APP_NAME = "ABB Polishing Studio"
    VERSION = "v2.0 Industrial"
    AUTHOR = "Robotic Solutions"

    # 文件系统配置 [cite: 3]
    # 使用 pathlib 处理跨平台路径
    HOME_DIR = Path.home() / ".abb_polishing_studio"
    LOG_FILE = HOME_DIR / "app.log"
    CONFIG_FILE = HOME_DIR / "config.json"

    # GUI 默认尺寸
    DEFAULT_WIDTH = 1400
    DEFAULT_HEIGHT = 850

    # 支持的文件格式 [cite: 4]
    SUPPORTED_FORMATS = [
        ("STL 模型文件", "*.stl"),
        ("NX 模型文件", "*.prt"),
        ("所有文件", "*.*")
    ]

    # 机器人型号数据库 [cite: 5]
    # 这里可以扩展为字典，存储更多机器人的物理参数（如最大臂展）
    SUPPORTED_ROBOTS = [
        "IRB 2600-12/1.85",
        "IRB 4600-40/2.55",
        "IRB 6700-300/2.70",
        "IRB 14000-0.5/0.9 (YuMi)",
        "IRB 1100-4/0.58",
        "自定义机器人"
    ]

    # 工具类型定义 [cite: 6]
    SUPPORTED_TOOLS = [
        "抛光轮 - 8mm",
        "抛光轮 - 10mm",
        "抛光轮 - 12mm",
        "砂带机 - 50mm",
        "气动打磨头 - 20mm"
    ]

    @classmethod
    def ensure_directories(cls):
        """确保必要的配置目录存在"""
        cls.HOME_DIR.mkdir(parents=True, exist_ok=True)