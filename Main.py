import tkinter as tk
from tkinter import messagebox
import sys

# 导入自定义模块
from Utils.config import AppConfig
from Utils.logger import logger
from Core.Core import PolishingCore
from GUI.main_window import PolishingStudioGUI


class PolishingAppController:
    """
    应用程序控制器
    负责连接 Core 逻辑与 GUI 界面
    """

    def __init__(self):
        # 1. 初始化配置与日志
        AppConfig.ensure_directories()
        logger.info("--- 正在启动 ABB Polishing Studio ---")

        # 2. 实例化核心引擎 (Headless/无界面逻辑)
        self.core = PolishingCore()

        # 3. 初始化主窗口 (注入 core)
        self.root = tk.Tk()
        self.app_gui = PolishingStudioGUI(self.root, core_engine=self.core)

        # 4. 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def run(self):
        """运行程序"""
        try:
            # 可以在这里检查环境，例如 trimesh 是否安装
            self._check_environment()

            logger.info("主事件循环启动")
            self.root.mainloop()
        except Exception as e:
            logger.critical(f"程序运行发生致命错误: {e}", exc_info=True)
            messagebox.showerror("致命错误", f"程序异常终止:\n{e}")
        finally:
            self.cleanup()

    def _check_environment(self):
        """环境依赖检查"""
        try:
            import trimesh
            import numpy
            logger.info("环境检查通过: numpy, trimesh 已加载")
        except ImportError as e:
            logger.warning(f"缺少可选依赖: {e}. 部分3D功能可能受限。")

    def on_exit(self):
        """退出时的处理"""
        if messagebox.askokcancel("退出程序", "是否确定退出 ABB Polishing Studio?"):
            logger.info("用户请求退出程序")
            self.root.destroy()

    def cleanup(self):
        """清理资源"""
        logger.info("--- 程序已关闭 ---")


if __name__ == "__main__":
    # 启动控制器
    controller = PolishingAppController()
    controller.run()