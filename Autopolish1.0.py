"""
ABB Polishing Studio - 工业级专业版 v8.1
集成NX STL加载、数学建模和高级RAPID代码生成系统

基于UG建模特征的高级抛光系统，包含：
1. NX/STL模型导入与几何特征分析
2. 数学建模与路径优化算法
3. 双工位智能化工艺规划
4. 工业级高级RAPID程序生成
5. 3D可视化预览与仿真系统

版本：PolishingStudio IRB 2600 抛光程序自动生成系统软件
"""

import json
import numpy as np
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, colorchooser
import os
import sys
import threading
import queue
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any, Union, Callable
import traceback
import math
import warnings
import webbrowser
import hashlib
import pickle
from pathlib import Path
from enum import Enum, auto
from abc import ABC, abstractmethod
import re
import base64
import zlib
import struct

# 忽略特定警告
warnings.filterwarnings('ignore', category=UserWarning)

# ==================== 3D模型处理库 ====================
try:
    import trimesh
    from trimesh import transformations
    from sklearn.cluster import DBSCAN, KMeans
    from scipy.spatial import cKDTree, ConvexHull, Delaunay
    from scipy.interpolate import splprep, splev, interp1d
    from scipy.optimize import minimize, least_squares
    from scipy.spatial.distance import cdist, pdist, squareform
    from scipy.linalg import norm, svd
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.patches import Circle, Ellipse

    TRIMESH_AVAILABLE = True
    MATPLOTLIB_AVAILABLE = True
except ImportError as e:
    print(f"警告: 需要安装必要的库。请运行: pip install trimesh scikit-learn scipy matplotlib")
    print(f"导入错误: {e}")
    TRIMESH_AVAILABLE = False
    MATPLOTLIB_AVAILABLE = False


# ==================== 工业级配置类 ====================
class AppConfig:
    """应用程序配置类 - 工业级"""
    # 版本信息
    VERSION = "ABB_IRB 2600 "
    BUILD_DATE = "2026-01-05"
    AUTHOR = "Robotic Solutions"

    # 应用程序设置
    APP_NAME = " Polishing Studio"
    MIN_WIDTH = 1600
    MIN_HEIGHT = 900
    DEFAULT_WIDTH = 1800
    DEFAULT_HEIGHT = 1000

    # 文件路径
    CONFIG_DIR = Path.home() / ".abb_polishing_studio_industrial"
    LOG_FILE = CONFIG_DIR / "app.log"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    TEMPLATE_DIR = CONFIG_DIR / "templates"

    # 支持的模型格式
    SUPPORTED_FORMATS = [
        ("NX STL文件", "*.stl"),
        ("STEP文件", "*.step;*.stp"),
        ("IGES文件", "*.iges;*.igs"),
        ("Parasolid文件", "*.x_t;*.x_b"),
        ("UG NX文件", "*.prt"),
        ("所有文件", "*.*")
    ]

    # 支持的机器人型号
    SUPPORTED_ROBOTS = [
        "IRB 2600-12/1.85",
        "IRB 4600-40/2.55",
        "IRB 6700-300/2.70",
        "IRB 14000-0.5/0.9",
        "IRB 1100-4/0.58",
        "IRB 6700F-200/2.70",
        "IRB 8700-550/3.20",
        "自定义机器人"
    ]

    # 工业级工具类型
    SUPPORTED_TOOLS = [
        "抛光轮 - 8mm",
        "抛光轮 - 10mm",
        "抛光轮 - 12mm",
        "砂带机 - 50mm",
        "砂带机 - 75mm",
        "角磨机 - 100mm",
        "自定义工具"
    ]

    @classmethod
    def ensure_dirs(cls):
        """确保配置目录存在"""
        cls.CONFIG_DIR.mkdir(exist_ok=True, parents=True)
        cls.TEMPLATE_DIR.mkdir(exist_ok=True, parents=True)


# ==================== 专业UI配色方案 ====================
class ProfessionalColors:
    """专业UI配色方案"""

    # 主色 - 品牌色（ABB蓝）
    PRIMARY = "#005596"  # ABB品牌蓝色，占界面30-40%
    PRIMARY_LIGHT = "#337AB7"
    PRIMARY_DARK = "#003D6B"
    PRIMARY_DARKER = "#002540"

    # 辅助色 - 功能区分色（绿色，用于已选状态、成功等）
    SECONDARY = "#07C160"  # 微信绿，用于功能区分，占10-20%
    SECONDARY_LIGHT = "#38D88C"
    SECONDARY_DARK = "#05A84E"
    SECONDARY_DARKER = "#048B41"

    # 中性色 - 梯度灰色系
    # 背景梯度
    BACKGROUND_LIGHTEST = "#FFFFFF"  # 白色背景
    BACKGROUND_LIGHTER = "#FAFAFA"  # 非常浅灰
    BACKGROUND_LIGHT = "#F5F5F5"  # 浅灰背景
    BACKGROUND = "#F0F0F0"  # 背景主色
    BACKGROUND_DARK = "#E0E0E0"  # 中灰背景
    BACKGROUND_DARKER = "#D0D0D0"  # 深灰背景

    # 文字梯度
    TEXT_PRIMARY = "#333333"  # 标题文字，最重要
    TEXT_SECONDARY = "#666666"  # 正文文字
    TEXT_TERTIARY = "#999999"  # 辅助文字
    TEXT_LIGHT = "#CCCCCC"  # 禁用文字
    TEXT_DISABLED = "#E0E0E0"  # 完全禁用

    # 边框梯度
    BORDER_LIGHT = "#E0E0E0"  # 浅边框
    BORDER = "#CCCCCC"  # 常规边框
    BORDER_DARK = "#9E9E9E"  # 深边框
    BORDER_DARKER = "#666666"  # 最深边框

    # 表面梯度（卡片、面板）
    SURFACE = "#FFFFFF"  # 白色表面
    SURFACE_LIGHT = "#FAFAFA"  # 浅表面
    SURFACE_DARK = "#F5F5F5"  # 深表面
    SURFACE_DARKER = "#F0F0F0"  # 更深表面

    # 功能色 - 场景区分
    SUCCESS = "#07C160"  # 成功场景
    SUCCESS_LIGHT = "#E8F8F0"
    SUCCESS_DARK = "#05A84E"

    WARNING = "#FF9500"  # 警告场景
    WARNING_LIGHT = "#FFF7E6"
    WARNING_DARK = "#E67E22"

    ERROR = "#FF4D4F"  # 错误/警示场景
    ERROR_LIGHT = "#FFF2F0"
    ERROR_DARK = "#E74C3C"

    INFO = "#1890FF"  # 信息场景
    INFO_LIGHT = "#E6F7FF"
    INFO_DARK = "#3498DB"

    # 交互色
    INTERACTIVE_PRIMARY = "#005596"  # 主要交互元素
    INTERACTIVE_SECONDARY = "#1890FF"  # 次要交互元素
    INTERACTIVE_HOVER = "#003D6B"  # 悬停状态
    INTERACTIVE_ACTIVE = "#002540"  # 激活状态
    INTERACTIVE_DISABLED = "#E0E0E0"  # 禁用状态

    # 代码编辑区
    CODE_BACKGROUND = "#1E1E1E"  # VS Code风格暗背景
    CODE_TEXT = "#D4D4D4"
    CODE_COMMENT = "#6A9955"
    CODE_KEYWORD = "#569CD6"
    CODE_STRING = "#CE9178"
    CODE_NUMBER = "#B5CEA8"
    CODE_FUNCTION = "#DCDCAA"
    CODE_VARIABLE = "#9CDCFE"

    # 图表色系
    CHART_COLORS = [
        "#005596", "#07C160", "#FF9500", "#FF4D4F", "#8E44AD",
        "#3498DB", "#27AE60", "#F39C12", "#E74C3C", "#566573"
    ]

    # 透明度
    @staticmethod
    def with_alpha(color, alpha=0.1):
        """为颜色添加透明度"""
        if isinstance(alpha, float):
            alpha = int(alpha * 255)

        # 如果是十六进制颜色
        if color.startswith('#'):
            if len(color) == 7:
                return color + f"{alpha:02x}"
            elif len(color) == 9:
                return color[:-2] + f"{alpha:02x}"

        return color

    # 对比度检查
    @staticmethod
    def get_contrast_ratio(color1, color2):
        """计算两个颜色的对比度"""

        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join([c * 2 for c in hex_color])
            return tuple(int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4))

        def luminance(rgb):
            r, g, b = rgb
            rs = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            gs = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            bs = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs

        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        l1 = luminance(rgb1)
        l2 = luminance(rgb2)

        lighter = max(l1, l2)
        darker = min(l1, l2)

        return (lighter + 0.05) / (darker + 0.05)


# ==================== 专业UI组件 ====================
class ProfessionalFrame(tk.Frame):
    """专业框架组件"""

    def __init__(self, parent, padding=16, bg=None, **kwargs):
        bg = bg or ProfessionalColors.BACKGROUND
        super().__init__(parent, bg=bg, **kwargs)
        self.padding = padding

    def add_margin(self, widget, **kwargs):
        """为组件添加外边距"""
        widget.pack(padx=self.padding, pady=self.padding, **kwargs)

    def add_padding(self, widget, **kwargs):
        """为组件添加内边距"""
        frame = tk.Frame(self, bg=self.cget('bg'))
        frame.pack(fill="both", expand=True)
        widget.pack(in_=frame, padx=self.padding, pady=self.padding, **kwargs)


class ProfessionalCard(tk.Frame):
    """专业卡片组件"""

    def __init__(self, parent, title="", subtitle="", padding=16,
                 bg=ProfessionalColors.SURFACE, show_border=True,
                 elevation=1, corner_radius=0, **kwargs):
        super().__init__(parent, **kwargs)

        # 配置卡片样式
        self.configure(
            bg=ProfessionalColors.BACKGROUND,
            highlightbackground=ProfessionalColors.BORDER_LIGHT,
            highlightthickness=1 if show_border else 0
        )

        # 创建阴影效果
        if elevation > 0:
            shadow_color = ProfessionalColors.with_alpha("#000000", 0.1)
            self.shadow = tk.Frame(
                self,
                bg=shadow_color,
                relief="flat"
            )
            self.shadow.place(x=2, y=2, relwidth=1.0, relheight=1.0)
            self.shadow.lower()

        # 卡片内容容器
        self.content_frame = tk.Frame(self, bg=bg)
        self.content_frame.pack(fill="both", expand=True, padx=1, pady=1)

        # 标题区域（如果有标题）
        if title:
            self.title_frame = tk.Frame(
                self.content_frame,
                bg=ProfessionalColors.SURFACE_DARK,
                height=48
            )
            self.title_frame.pack(fill="x", pady=(0, padding))
            self.title_frame.pack_propagate(False)

            # 标题内容
            title_content = tk.Frame(self.title_frame, bg=ProfessionalColors.SURFACE_DARK)
            title_content.pack(fill="both", expand=True, padx=padding)

            # 主标题
            self.title_label = tk.Label(
                title_content,
                text=title,
                font=("微软雅黑", 12, "bold"),
                bg=ProfessionalColors.SURFACE_DARK,
                fg=ProfessionalColors.TEXT_PRIMARY,
                anchor="w"
            )
            self.title_label.pack(side="left", fill="x", expand=True)

            # 副标题
            if subtitle:
                self.subtitle_label = tk.Label(
                    title_content,
                    text=subtitle,
                    font=("微软雅黑", 10),
                    bg=ProfessionalColors.SURFACE_DARK,
                    fg=ProfessionalColors.TEXT_TERTIARY,
                    anchor="e"
                )
                self.subtitle_label.pack(side="right")

        # 内容区域
        self.body_frame = tk.Frame(self.content_frame, bg=bg)
        self.body_frame.pack(fill="both", expand=True, padx=padding, pady=(0, padding))


class ProfessionalButton(tk.Frame):
    """专业按钮组件"""

    def __init__(self, parent, text="", command=None, icon=None,
                 variant="primary", size="medium", width=None,
                 tooltip="", disabled=False, **kwargs):
        super().__init__(parent, **kwargs)

        self.text = text
        self.command = command
        self.icon = icon
        self.variant = variant
        self.size = size
        self.tooltip_text = tooltip
        self.disabled = disabled

        # 获取颜色配置
        self.colors = self._get_variant_colors()

        # 获取尺寸配置
        size_params = self._get_size_params()

        # 配置按钮框架
        self.configure(
            bg=ProfessionalColors.BACKGROUND_LIGHT,
            cursor="pointer" if not disabled else "arrow"
        )

        # 按钮主体
        self.button_frame = tk.Frame(
            self,
            bg=self.colors['bg'],
            relief="flat",
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        self.button_frame.pack(fill="both", expand=True)

        # 按钮内容
        content_padding = size_params['padding']
        content_frame = tk.Frame(self.button_frame, bg=self.colors['bg'])
        content_frame.pack(fill="both", expand=True,
                           padx=content_padding, pady=content_padding)

        # 图标（如果有）
        if self.icon:
            self.icon_label = tk.Label(
                content_frame,
                text=self.icon,
                font=("Segoe UI Symbol", size_params['icon_size']),
                bg=self.colors['bg'],
                fg=self.colors['fg']
            )
            self.icon_label.pack(side="left", padx=(0, 6))

        # 文字
        self.text_label = tk.Label(
            content_frame,
            text=self.text,
            font=("微软雅黑", size_params['font_size'], "bold"),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        )
        self.text_label.pack(side="left", fill="x", expand=True)

        # 如果是禁用状态
        if disabled:
            self._set_disabled_state()

        # 绑定事件
        if not disabled:
            self._bind_events()

    def _get_variant_colors(self):
        """获取变体颜色"""
        variants = {
            "primary": {
                'bg': ProfessionalColors.INTERACTIVE_PRIMARY,
                'fg': "white",
                'hover': ProfessionalColors.INTERACTIVE_HOVER,
                'active': ProfessionalColors.INTERACTIVE_ACTIVE,
                'border': ProfessionalColors.PRIMARY_DARK
            },
            "secondary": {
                'bg': ProfessionalColors.SECONDARY,
                'fg': "white",
                'hover': ProfessionalColors.SECONDARY_DARK,
                'active': ProfessionalColors.SECONDARY_DARKER,
                'border': ProfessionalColors.SECONDARY_DARK
            },
            "success": {
                'bg': ProfessionalColors.SUCCESS,
                'fg': "white",
                'hover': ProfessionalColors.SUCCESS_DARK,
                'active': "#048B41",
                'border': ProfessionalColors.SUCCESS_DARK
            },
            "warning": {
                'bg': ProfessionalColors.WARNING,
                'fg': "white",
                'hover': ProfessionalColors.WARNING_DARK,
                'active': "#D35400",
                'border': ProfessionalColors.WARNING_DARK
            },
            "error": {
                'bg': ProfessionalColors.ERROR,
                'fg': "white",
                'hover': ProfessionalColors.ERROR_DARK,
                'active': "#C0392B",
                'border': ProfessionalColors.ERROR_DARK
            },
            "info": {
                'bg': ProfessionalColors.INFO,
                'fg': "white",
                'hover': ProfessionalColors.INFO_DARK,
                'active': "#2980B9",
                'border': ProfessionalColors.INFO_DARK
            },
            "ghost": {
                'bg': ProfessionalColors.SURFACE,
                'fg': ProfessionalColors.TEXT_PRIMARY,
                'hover': ProfessionalColors.BACKGROUND_LIGHT,
                'active': ProfessionalColors.BACKGROUND_DARK,
                'border': ProfessionalColors.BORDER_LIGHT
            },
            "disabled": {
                'bg': ProfessionalColors.INTERACTIVE_DISABLED,
                'fg': ProfessionalColors.TEXT_DISABLED,
                'hover': ProfessionalColors.INTERACTIVE_DISABLED,
                'active': ProfessionalColors.INTERACTIVE_DISABLED,
                'border': ProfessionalColors.BORDER_LIGHT
            }
        }

        if self.disabled:
            return variants["disabled"]
        return variants.get(self.variant, variants["primary"])

    def _get_size_params(self):
        """获取尺寸参数"""
        sizes = {
            "small": {'font_size': 10, 'icon_size': 12, 'padding': 6},
            "medium": {'font_size': 11, 'icon_size': 14, 'padding': 8},
            "large": {'font_size': 12, 'icon_size': 16, 'padding': 12}
        }
        return sizes.get(self.size, sizes["medium"])

    def _set_disabled_state(self):
        """设置为禁用状态"""
        colors = self.colors
        self.button_frame.configure(
            bg=colors['bg'],
            highlightbackground=colors['border']
        )
        for child in self.button_frame.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=colors['bg'])
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Label):
                        grandchild.configure(bg=colors['bg'], fg=colors['fg'])

    def _bind_events(self):
        """绑定事件"""
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.button_frame.bind("<Enter>", self._on_enter)
        self.button_frame.bind("<Leave>", self._on_leave)
        self.button_frame.bind("<Button-1>", self._on_press)
        self.button_frame.bind("<ButtonRelease-1>", self._on_release)

    def _on_enter(self, event):
        """鼠标进入"""
        colors = self.colors
        self.button_frame.configure(bg=colors['hover'])
        for child in self.button_frame.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=colors['hover'])
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Label):
                        grandchild.configure(bg=colors['hover'])

    def _on_leave(self, event):
        """鼠标离开"""
        colors = self.colors
        self.button_frame.configure(bg=colors['bg'])
        for child in self.button_frame.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=colors['bg'])
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Label):
                        grandchild.configure(bg=colors['bg'])

    def _on_press(self, event):
        """鼠标按下"""
        colors = self.colors
        self.button_frame.configure(bg=colors['active'])
        for child in self.button_frame.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=colors['active'])
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Label):
                        grandchild.configure(bg=colors['active'])

    def _on_release(self, event):
        """鼠标释放"""
        colors = self.colors
        self.button_frame.configure(bg=colors['hover'])
        for child in self.button_frame.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=colors['hover'])
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Label):
                        grandchild.configure(bg=colors['hover'])

        # 执行命令
        if self.command:
            self.command()


class ProfessionalEntry(tk.Frame):
    """专业输入框组件"""

    def __init__(self, parent, label="", placeholder="", textvariable=None,
                 width=30, padding=8, show_label=True, **kwargs):
        super().__init__(parent, **kwargs)

        self.configure(bg=ProfessionalColors.BACKGROUND_LIGHT)

        # 标签（如果有）
        if show_label and label:
            self.label = tk.Label(
                self,
                text=label,
                font=("微软雅黑", 10),
                bg=ProfessionalColors.BACKGROUND_LIGHT,
                fg=ProfessionalColors.TEXT_SECONDARY,
                anchor="w"
            )
            self.label.pack(fill="x", pady=(0, 4))

        # 输入框容器
        entry_frame = tk.Frame(self, bg=ProfessionalColors.BACKGROUND_LIGHT)
        entry_frame.pack(fill="x")

        # 输入框
        self.entry = tk.Entry(
            entry_frame,
            textvariable=textvariable,
            font=("微软雅黑", 10),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_PRIMARY,
            relief="solid",
            borderwidth=1,
            width=width,
            insertbackground=ProfessionalColors.PRIMARY
        )
        self.entry.pack(fill="x", padx=padding, pady=padding)

        # 占位符文本
        if placeholder and (not textvariable or not textvariable.get()):
            self.placeholder = placeholder
            self.entry.insert(0, placeholder)
            self.entry.config(fg=ProfessionalColors.TEXT_TERTIARY)
            self.entry.bind("<FocusIn>", self._on_focus_in)
            self.entry.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, event):
        """焦点进入"""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=ProfessionalColors.TEXT_PRIMARY)

    def _on_focus_out(self, event):
        """焦点离开"""
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=ProfessionalColors.TEXT_TERTIARY)

    def get(self):
        """获取输入值"""
        value = self.entry.get()
        if value == self.placeholder:
            return ""
        return value

    def set(self, value):
        """设置输入值"""
        self.entry.delete(0, tk.END)
        if value:
            self.entry.insert(0, value)
            self.entry.config(fg=ProfessionalColors.TEXT_PRIMARY)
        elif hasattr(self, 'placeholder'):
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=ProfessionalColors.TEXT_TERTIARY)


class ProfessionalComboBox(tk.Frame):
    """专业下拉框组件"""

    def __init__(self, parent, label="", values=None, textvariable=None,
                 width=20, padding=8, show_label=True, **kwargs):
        super().__init__(parent, **kwargs)

        self.configure(bg=ProfessionalColors.BACKGROUND_LIGHT)

        # 标签（如果有）
        if show_label and label:
            self.label = tk.Label(
                self,
                text=label,
                font=("微软雅黑", 10),
                bg=ProfessionalColors.BACKGROUND_LIGHT,
                fg=ProfessionalColors.TEXT_SECONDARY,
                anchor="w"
            )
            self.label.pack(fill="x", pady=(0, 4))

        # 下拉框容器
        combo_frame = tk.Frame(self, bg=ProfessionalColors.BACKGROUND_LIGHT)
        combo_frame.pack(fill="x")

        # 下拉框
        self.combo = ttk.Combobox(
            combo_frame,
            textvariable=textvariable,
            values=values or [],
            state="readonly",
            width=width,
            font=("微软雅黑", 10)
        )
        self.combo.pack(fill="x", padx=padding, pady=padding)

        # 配置样式
        style = ttk.Style()
        style.theme_use('clam')

        # 配置下拉框样式
        style.configure("TCombobox",
                        fieldbackground=ProfessionalColors.SURFACE,
                        background=ProfessionalColors.SURFACE,
                        foreground=ProfessionalColors.TEXT_PRIMARY,
                        bordercolor=ProfessionalColors.BORDER,
                        lightcolor=ProfessionalColors.BORDER_LIGHT,
                        darkcolor=ProfessionalColors.BORDER_DARK,
                        arrowsize=12
                        )

        style.map("TCombobox",
                  fieldbackground=[('readonly', ProfessionalColors.SURFACE)],
                  selectbackground=[('readonly', ProfessionalColors.PRIMARY)],
                  selectforeground=[('readonly', 'white')]
                  )


# ==================== 主应用程序类（优化UI版） ====================
class ABBPolishingStudioProfessional:
    """ABB Polishing Studio - 专业版主应用程序"""

    def __init__(self):
        # 初始化配置
        AppConfig.ensure_dirs()

        # 创建日志和配置
        self.logger = self._create_logger()
        self.config = self._load_config()

        # 初始化组件
        self.colors = ProfessionalColors()  # 修复这里
        self.math_model = PolishingMathematicalModel()
        self.path_planner = None

        # 创建主窗口
        self.root = tk.Tk()
        self._setup_main_window()

        # 初始化处理器
        self.nx_processor = NXSTLProcessor()
        self.rapid_generator = IndustrialRAPIDGenerator(self.logger)

        # 数据存储
        self.current_model = None
        self.model_metadata = {}
        self.features = []
        self.paths = {}
        self.generated_code = ""

        # 数学建模参数
        self.math_params = {
            'surface_curvature': 0.01,
            'material_hardness': 200.0,
            'tool_wear_factor': 0.001,
            'force_distribution': 'uniform',
            'optimization_level': 'high'
        }

        # 创建UI
        self._create_ui()

        # 绑定事件
        self._bind_events()

    def _create_logger(self):
        """创建日志系统"""

        class SimpleLogger:
            def info(self, msg): print(f"[INFO] {msg}")

            def error(self, msg): print(f"[ERROR] {msg}")

            def warning(self, msg): print(f"[WARNING] {msg}")

        return SimpleLogger()

    def _load_config(self):
        """加载配置"""
        return {
            'recent_files': [],
            'robot_model': AppConfig.SUPPORTED_ROBOTS[0],
            'tool_type': AppConfig.SUPPORTED_TOOLS[0],
            'nx_processing': True
        }

    def _setup_main_window(self):
        """设置主窗口"""
        self.root.title(f"{AppConfig.APP_NAME} {AppConfig.VERSION}")
        self.root.geometry("1600x900")
        self.root.minsize(1400, 800)

        # 居中显示
        self.root.eval('tk::PlaceWindow . center')

        # 设置窗口图标
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

        # 设置窗口背景
        self.root.configure(bg=self.colors.BACKGROUND)

    def _create_ui(self):
        """创建专业用户界面"""
        # 创建主容器
        self.main_container = tk.Frame(
            self.root,
            bg=self.colors.BACKGROUND,
            padx=16,  # 呼吸感：屏幕边缘留白
            pady=16
        )
        self.main_container.pack(fill="both", expand=True)

        # 创建标题栏
        self._create_title_bar()

        # 创建主内容区域
        self._create_main_content()

        # 创建状态栏
        self._create_status_bar()

    def _create_title_bar(self):
        """创建专业标题栏"""
        title_frame = tk.Frame(
            self.main_container,
            bg=self.colors.PRIMARY,  # 主品牌色
            height=64  # 高度适中
        )
        title_frame.pack(fill="x", pady=(0, 16))
        title_frame.pack_propagate(False)

        # 标题内容（两侧留白）
        title_content = tk.Frame(title_frame, bg=self.colors.PRIMARY)
        title_content.pack(fill="both", expand=True, padx=20)

        # 左侧：品牌标识
        left_frame = tk.Frame(title_content, bg=self.colors.PRIMARY)
        left_frame.pack(side="left", fill="y")

        # 品牌图标
        icon_frame = tk.Frame(left_frame, bg=self.colors.PRIMARY)
        icon_frame.pack(side="left", padx=(0, 12))

        # 使用文本图标（实际使用中可替换为图片）
        icon_label = tk.Label(
            icon_frame,
            text="🏭",
            font=("Segoe UI", 24),
            bg=self.colors.PRIMARY,
            fg="white"
        )
        icon_label.pack()

        # 品牌文字
        brand_frame = tk.Frame(left_frame, bg=self.colors.PRIMARY)
        brand_frame.pack(side="left")

        brand_title = tk.Label(
            brand_frame,
            text=AppConfig.APP_NAME,
            font=("微软雅黑", 18, "bold"),
            bg=self.colors.PRIMARY,
            fg="white"
        )
        brand_title.pack(anchor="w")

        brand_subtitle = tk.Label(
            brand_frame,
            text=f"{AppConfig.VERSION} | 工业级机器人抛光解决方案",
            font=("微软雅黑", 10),
            bg=self.colors.PRIMARY,
            fg=ProfessionalColors.with_alpha("#FFFFFF", 0.8)  # 半透明白色
        )
        brand_subtitle.pack(anchor="w")

        # 右侧：操作状态
        right_frame = tk.Frame(title_content, bg=self.colors.PRIMARY)
        right_frame.pack(side="right", fill="y")

        # 模型状态指示器
        status_card = tk.Frame(
            right_frame,
            bg=ProfessionalColors.with_alpha("#FFFFFF", 0.15),  # 半透明背景
            relief="flat"
        )
        status_card.pack(side="right", padx=(12, 0))

        self.model_status_icon = tk.Label(
            status_card,
            text="○",
            font=("Segoe UI", 12),
            bg=ProfessionalColors.with_alpha("#FFFFFF", 0.15),
            fg=self.colors.WARNING  # 初始为警告色（未加载）
        )
        self.model_status_icon.pack(side="left", padx=(8, 4), pady=4)

        self.model_status_text = tk.Label(
            status_card,
            text="未加载模型",
            font=("微软雅黑", 10),
            bg=ProfessionalColors.with_alpha("#FFFFFF", 0.15),
            fg="white"
        )
        self.model_status_text.pack(side="left", padx=(0, 8), pady=4)

    def _create_main_content(self):
        """创建主内容区域"""
        # 使用专业框架
        main_frame = ProfessionalFrame(
            self.main_container,
            padding=0,  # 在外层框架控制间距
            bg=self.colors.BACKGROUND
        )
        main_frame.pack(fill="both", expand=True)

        # 创建水平分割
        self._create_horizontal_layout(main_frame)

    def _create_horizontal_layout(self, parent):
        """创建水平布局"""
        # 左侧面板容器
        left_container = ProfessionalFrame(
            parent,
            bg=self.colors.BACKGROUND_LIGHT,
            width=380  # 固定宽度
        )
        left_container.pack(side="left", fill="y")
        left_container.pack_propagate(False)

        # 右侧面板容器
        right_container = ProfessionalFrame(
            parent,
            bg=self.colors.BACKGROUND,
            padding=16
        )
        right_container.pack(side="right", fill="both", expand=True, padx=(16, 0))

        # 创建左侧面板
        self._create_left_panel(left_container)

        # 创建右侧面板
        self._create_right_panel(right_container)

    def _create_left_panel(self, parent):
        """创建左侧控制面板"""
        # 创建滚动区域
        canvas_frame = ProfessionalFrame(parent, padding=0)
        canvas_frame.pack(fill="both", expand=True)

        # 滚动画布
        canvas = tk.Canvas(
            canvas_frame,
            bg=self.colors.BACKGROUND_LIGHT,
            highlightthickness=0,
            relief="flat"
        )
        scrollbar = tk.Scrollbar(
            canvas_frame,
            orient="vertical",
            command=canvas.yview,
            bg=self.colors.BACKGROUND_DARK
        )

        # 可滚动内容
        scrollable_frame = tk.Frame(canvas, bg=self.colors.BACKGROUND_LIGHT)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=360)
        canvas.configure(yscrollcommand=scrollbar.set)

        # 布局
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # 内容区域
        content_frame = ProfessionalFrame(
            scrollable_frame,
            padding=16,
            bg=self.colors.BACKGROUND_LIGHT
        )
        content_frame.pack(fill="both", expand=True)

        # 创建控制卡片
        self._create_control_cards(content_frame)

    def _create_control_cards(self, parent):
        """创建控制卡片"""
        # 1. 文件处理卡片
        file_card = ProfessionalCard(
            parent,
            title="模型文件",
            subtitle="导入与分析",
            padding=12
        )
        file_card.pack(fill="x", pady=(0, 16))
        self._create_file_card_content(file_card.body_frame)

        # 2. 机器人配置卡片
        robot_card = ProfessionalCard(
            parent,
            title="机器人配置",
            subtitle="运动参数",
            padding=12
        )
        robot_card.pack(fill="x", pady=(0, 16))
        self._create_robot_card_content(robot_card.body_frame)

        # 3. 工具配置卡片
        tool_card = ProfessionalCard(
            parent,
            title="工具配置",
            subtitle="抛光参数",
            padding=12
        )
        tool_card.pack(fill="x", pady=(0, 16))
        self._create_tool_card_content(tool_card.body_frame)

        # 4. 路径规划卡片
        path_card = ProfessionalCard(
            parent,
            title="路径规划",
            subtitle="智能生成",
            padding=12
        )
        path_card.pack(fill="x", pady=(0, 16))
        self._create_path_card_content(path_card.body_frame)

        # 5. 代码生成卡片
        code_card = ProfessionalCard(
            parent,
            title="代码生成",
            subtitle="RAPID程序",
            padding=12
        )
        code_card.pack(fill="x")
        self._create_code_card_content(code_card.body_frame)

    def _create_file_card_content(self, parent):
        """创建文件卡片内容"""
        # 文件选择区域
        file_select_frame = tk.Frame(parent, bg=ProfessionalColors.SURFACE)
        file_select_frame.pack(fill="x", pady=(0, 12))

        # 文件路径显示
        self.file_path_var = tk.StringVar()
        file_entry = ProfessionalEntry(
            file_select_frame,
            placeholder="选择STL文件...",
            textvariable=self.file_path_var,
            width=28,
            padding=8,
            show_label=False
        )
        file_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # 浏览按钮
        browse_btn = ProfessionalButton(
            file_select_frame,
            text="浏览",
            command=self.browse_file,
            variant="ghost",
            size="small"
        )
        browse_btn.pack(side="right")

        # 处理选项
        options_frame = tk.Frame(parent, bg=ProfessionalColors.SURFACE)
        options_frame.pack(fill="x", pady=(0, 12))

        self.nx_processing_var = tk.BooleanVar(value=True)
        nx_check = tk.Checkbutton(
            options_frame,
            text="启用NX特殊处理",
            variable=self.nx_processing_var,
            font=("微软雅黑", 10),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_PRIMARY,
            selectcolor=ProfessionalColors.SURFACE,
            activebackground=ProfessionalColors.SURFACE,
            activeforeground=ProfessionalColors.TEXT_PRIMARY
        )
        nx_check.pack(anchor="w")

        # 加载按钮
        load_btn = ProfessionalButton(
            parent,
            text="加载模型",
            command=self.load_model,
            variant="primary",
            size="medium"
        )
        load_btn.pack(fill="x", pady=(0, 12))

        # 模型信息显示
        info_frame = tk.Frame(parent, bg=ProfessionalColors.SURFACE_DARK)
        info_frame.pack(fill="x")

        self.model_info_text = tk.Text(
            info_frame,
            height=8,
            font=("Consolas", 9),
            bg=ProfessionalColors.SURFACE_DARK,
            fg=ProfessionalColors.TEXT_SECONDARY,
            relief="flat",
            borderwidth=0,
            wrap="word"
        )
        self.model_info_text.pack(fill="both", padx=1, pady=1)
        self.model_info_text.insert("1.0", "等待加载模型...")
        self.model_info_text.configure(state="disabled")

    def _create_robot_card_content(self, parent):
        """创建机器人卡片内容"""
        # 机器人型号选择
        model_frame = tk.Frame(parent, bg=ProfessionalColors.SURFACE)
        model_frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            model_frame,
            text="机器人型号",
            font=("微软雅黑", 10),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_SECONDARY
        ).pack(side="left")

        self.robot_model_var = tk.StringVar(value=AppConfig.SUPPORTED_ROBOTS[0])
        robot_combo = ProfessionalComboBox(
            model_frame,
            values=AppConfig.SUPPORTED_ROBOTS,
            textvariable=self.robot_model_var,
            width=18,
            padding=0,
            show_label=False
        )
        robot_combo.pack(side="right")

        # 机器人参数信息
        info_frame = tk.Frame(parent, bg=ProfessionalColors.SURFACE)
        info_frame.pack(fill="x")

        self.robot_info_text = tk.Text(
            info_frame,
            height=6,
            font=("微软雅黑", 9),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_TERTIARY,
            relief="flat",
            borderwidth=0,
            wrap="word"
        )
        self.robot_info_text.pack(fill="both")
        self.robot_info_text.insert("1.0", self._get_robot_info())
        self.robot_info_text.configure(state="disabled")

    def _get_robot_info(self):
        """获取机器人信息"""
        robot_info = {
            "IRB 2600-12/1.85": "负载: 12kg | 范围: 1850mm\n精度: ±0.05mm\n应用: 中小型工件",
            "IRB 4600-40/2.55": "负载: 40kg | 范围: 2550mm\n精度: ±0.05mm\n应用: 中型工件",
            "IRB 6700-300/2.70": "负载: 300kg | 范围: 2700mm\n精度: ±0.06mm\n应用: 大型工件",
            "IRB 14000-0.5/0.9": "负载: 0.5kg | 范围: 900mm\n精度: ±0.02mm\n应用: 精密抛光",
            "IRB 1100-4/0.58": "负载: 4kg | 范围: 580mm\n精度: ±0.02mm\n应用: 紧凑空间",
            "IRB 6700F-200/2.70": "负载: 200kg | 范围: 2700mm\n精度: ±0.06mm\n应用: 重型抛光",
            "IRB 8700-550/3.20": "负载: 550kg | 范围: 3200mm\n精度: ±0.08mm\n应用: 超大型工件",
            "自定义机器人": "请配置自定义参数"
        }
        return robot_info.get(self.robot_model_var.get(), "选择机器人型号查看参数")

    def _create_tool_card_content(self, parent):
        """创建工具卡片内容"""
        # 工具类型选择
        type_frame = tk.Frame(parent, bg=ProfessionalColors.SURFACE)
        type_frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            type_frame,
            text="工具类型",
            font=("微软雅黑", 10),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_SECONDARY
        ).pack(side="left")

        self.tool_type_var = tk.StringVar(value=AppConfig.SUPPORTED_TOOLS[0])
        tool_combo = ProfessionalComboBox(
            type_frame,
            values=AppConfig.SUPPORTED_TOOLS,
            textvariable=self.tool_type_var,
            width=18,
            padding=0,
            show_label=False
        )
        tool_combo.pack(side="right")

        # 工具参数
        params_frame = tk.Frame(parent, bg=ProfessionalColors.SURFACE)
        params_frame.pack(fill="x", pady=(0, 8))

        # 工具直径
        tk.Label(
            params_frame,
            text="工具直径",
            font=("微软雅黑", 10),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_SECONDARY
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.tool_diameter_var = tk.DoubleVar(value=8.0)
        diameter_spin = tk.Spinbox(
            params_frame,
            from_=2.0,
            to=20.0,
            increment=0.5,
            textvariable=self.tool_diameter_var,
            width=8,
            font=("微软雅黑", 10),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_PRIMARY,
            relief="solid",
            borderwidth=1,
            buttonbackground=ProfessionalColors.BACKGROUND_LIGHT
        )
        diameter_spin.grid(row=0, column=1, sticky="e", pady=(0, 8))
        tk.Label(
            params_frame,
            text="mm",
            font=("微软雅黑", 10),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_TERTIARY
        ).grid(row=0, column=2, sticky="w", padx=(4, 0), pady=(0, 8))

        # 工具长度
        tk.Label(
            params_frame,
            text="工具长度",
            font=("微软雅黑", 10),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_SECONDARY
        ).grid(row=1, column=0, sticky="w")

        self.tool_length_var = tk.DoubleVar(value=200.0)
        length_spin = tk.Spinbox(
            params_frame,
            from_=50.0,
            to=500.0,
            increment=10.0,
            textvariable=self.tool_length_var,
            width=8,
            font=("微软雅黑", 10),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_PRIMARY,
            relief="solid",
            borderwidth=1,
            buttonbackground=ProfessionalColors.BACKGROUND_LIGHT
        )
        length_spin.grid(row=1, column=1, sticky="e")
        tk.Label(
            params_frame,
            text="mm",
            font=("微软雅黑", 10),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_TERTIARY
        ).grid(row=1, column=2, sticky="w", padx=(4, 0))

    def _create_path_card_content(self, parent):
        """创建路径卡片内容"""
        # 路径类型选择
        type_frame = tk.Frame(parent, bg=ProfessionalColors.SURFACE)
        type_frame.pack(fill="x", pady=(0, 12))

        self.path_type_var = tk.StringVar(value="adaptive")

        adaptive_btn = ProfessionalButton(
            type_frame,
            text="自适应",
            command=lambda: self.path_type_var.set("adaptive"),
            variant="ghost" if self.path_type_var.get() != "adaptive" else "secondary",
            size="small"
        )
        adaptive_btn.pack(side="left", padx=(0, 8))

        parallel_btn = ProfessionalButton(
            type_frame,
            text="平行线",
            command=lambda: self.path_type_var.set("parallel"),
            variant="ghost" if self.path_type_var.get() != "parallel" else "secondary",
            size="small"
        )
        parallel_btn.pack(side="left")

        # 路径参数
        param_frame = tk.Frame(parent, bg=ProfessionalColors.SURFACE)
        param_frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            param_frame,
            text="步距比例",
            font=("微软雅黑", 10),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_SECONDARY
        ).pack(side="left")

        self.stepover_var = tk.DoubleVar(value=0.5)
        stepover_scale = tk.Scale(
            param_frame,
            from_=0.1,
            to=0.8,
            resolution=0.05,
            variable=self.stepover_var,
            orient="horizontal",
            length=180,
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_PRIMARY,
            highlightthickness=0,
            troughcolor=ProfessionalColors.BACKGROUND_LIGHT,
            sliderrelief="flat",
            sliderlength=20
        )
        stepover_scale.pack(side="right")

        # 生成按钮
        generate_btn = ProfessionalButton(
            parent,
            text="生成抛光路径",
            command=self.generate_paths,
            variant="warning",
            size="medium"
        )
        generate_btn.pack(fill="x", pady=(0, 12))

        # 路径信息
        info_frame = tk.Frame(parent, bg=ProfessionalColors.SURFACE)
        info_frame.pack(fill="x")

        self.path_info_text = tk.Text(
            info_frame,
            height=6,
            font=("微软雅黑", 9),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_TERTIARY,
            relief="flat",
            borderwidth=0,
            wrap="word"
        )
        self.path_info_text.pack(fill="both")
        self.path_info_text.insert("1.0", "等待生成路径...")
        self.path_info_text.configure(state="disabled")

    def _create_code_card_content(self, parent):
        """创建代码卡片内容"""
        # 程序名称
        name_frame = tk.Frame(parent, bg=ProfessionalColors.SURFACE)
        name_frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            name_frame,
            text="程序名称",
            font=("微软雅黑", 10),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_SECONDARY
        ).pack(side="left")

        self.program_name_var = tk.StringVar(value="Polishing_Program")
        name_entry = ProfessionalEntry(
            name_frame,
            textvariable=self.program_name_var,
            width=18,
            padding=0,
            show_label=False
        )
        name_entry.pack(side="right")

        # 代码选项
        options_frame = tk.Frame(parent, bg=ProfessionalColors.SURFACE)
        options_frame.pack(fill="x", pady=(0, 12))

        self.include_io_var = tk.BooleanVar(value=True)
        io_check = tk.Checkbutton(
            options_frame,
            text="IO控制",
            variable=self.include_io_var,
            font=("微软雅黑", 10),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_PRIMARY,
            selectcolor=ProfessionalColors.SURFACE,
            activebackground=ProfessionalColors.SURFACE,
            activeforeground=ProfessionalColors.TEXT_PRIMARY
        )
        io_check.pack(side="left", padx=(0, 16))

        self.include_safety_var = tk.BooleanVar(value=True)
        safety_check = tk.Checkbutton(
            options_frame,
            text="安全检查",
            variable=self.include_safety_var,
            font=("微软雅黑", 10),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_PRIMARY,
            selectcolor=ProfessionalColors.SURFACE,
            activebackground=ProfessionalColors.SURFACE,
            activeforeground=ProfessionalColors.TEXT_PRIMARY
        )
        safety_check.pack(side="left")

        # 按钮区域
        button_frame = tk.Frame(parent, bg=ProfessionalColors.SURFACE)
        button_frame.pack(fill="x", pady=(0, 12))

        generate_btn = ProfessionalButton(
            button_frame,
            text="生成代码",
            command=self.generate_code,
            variant="primary",
            size="medium"
        )
        generate_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        export_btn = ProfessionalButton(
            button_frame,
            text="导出",
            command=self.export_program,
            variant="success",
            size="medium"
        )
        export_btn.pack(side="right")

        # 一键执行按钮
        execute_btn = ProfessionalButton(
            parent,
            text="执行完整流程",
            command=self.execute_full_process,
            variant="info",
            size="large"
        )
        execute_btn.pack(fill="x")

    def _create_right_panel(self, parent):
        """创建右侧显示面板"""
        # 创建选项卡容器
        tab_container = tk.Frame(parent, bg=ProfessionalColors.BACKGROUND)
        tab_container.pack(fill="both", expand=True)

        # 创建选项卡控件
        self.tab_control = ttk.Notebook(tab_container)
        self.tab_control.pack(fill="both", expand=True)

        # 配置选项卡样式
        style = ttk.Style()
        style.theme_use('clam')

        style.configure("TNotebook",
                        background=ProfessionalColors.BACKGROUND,
                        borderwidth=0
                        )
        style.configure("TNotebook.Tab",
                        background=ProfessionalColors.BACKGROUND_LIGHT,
                        foreground=ProfessionalColors.TEXT_SECONDARY,
                        padding=[12, 8],
                        font=("微软雅黑", 10)
                        )
        style.map("TNotebook.Tab",
                  background=[("selected", ProfessionalColors.SURFACE)],
                  foreground=[("selected", ProfessionalColors.TEXT_PRIMARY)]
                  )

        # 创建各个选项卡
        self._create_tab_3d_preview()
        self._create_tab_code_preview()
        self._create_tab_model_info()
        self._create_tab_path_preview()

    def _create_tab_3d_preview(self):
        """创建3D预览选项卡"""
        self.tab_3d = tk.Frame(self.tab_control, bg=ProfessionalColors.CODE_BACKGROUND)
        self.tab_control.add(self.tab_3d, text="3D预览")

        if not MATPLOTLIB_AVAILABLE:
            no_lib_label = tk.Label(
                self.tab_3d,
                text="需要安装matplotlib库以显示3D预览",
                font=("微软雅黑", 12),
                bg=ProfessionalColors.CODE_BACKGROUND,
                fg=ProfessionalColors.CODE_TEXT
            )
            no_lib_label.pack(expand=True, pady=40)
            return

        try:
            # 创建3D图形
            self.figure_3d = plt.Figure(figsize=(8, 6), dpi=100,
                                        facecolor=ProfessionalColors.CODE_BACKGROUND)
            self.ax_3d = self.figure_3d.add_subplot(111, projection='3d')

            # 配置3D轴
            self.ax_3d.set_facecolor(ProfessionalColors.CODE_BACKGROUND)

            # 创建画布
            self.canvas_3d = FigureCanvasTkAgg(self.figure_3d, self.tab_3d)
            self.canvas_3d.get_tk_widget().pack(fill="both", expand=True, padx=1, pady=1)

            # 初始设置
            self.ax_3d.set_xlabel('X (mm)', color=ProfessionalColors.CODE_TEXT)
            self.ax_3d.set_ylabel('Y (mm)', color=ProfessionalColors.CODE_TEXT)
            self.ax_3d.set_zlabel('Z (mm)', color=ProfessionalColors.CODE_TEXT)
            self.ax_3d.set_title('等待加载模型...', color=ProfessionalColors.CODE_TEXT)

            # 设置刻度颜色
            self.ax_3d.tick_params(axis='x', colors=ProfessionalColors.CODE_TEXT)
            self.ax_3d.tick_params(axis='y', colors=ProfessionalColors.CODE_TEXT)
            self.ax_3d.tick_params(axis='z', colors=ProfessionalColors.CODE_TEXT)

            # 设置网格
            self.ax_3d.grid(True, color=ProfessionalColors.with_alpha("#FFFFFF", 0.1))

            # 绘制初始图形
            self.canvas_3d.draw()

        except Exception as e:
            error_label = tk.Label(
                self.tab_3d,
                text=f"3D可视化初始化失败: {str(e)}",
                font=("微软雅黑", 10),
                bg=ProfessionalColors.ERROR_LIGHT,
                fg=ProfessionalColors.ERROR,
                padx=20,
                pady=10
            )
            error_label.pack(expand=True)

    def _create_tab_code_preview(self):
        """创建代码预览选项卡"""
        self.tab_code = tk.Frame(self.tab_control, bg=ProfessionalColors.BACKGROUND)
        self.tab_control.add(self.tab_code, text="代码预览")

        # 工具栏
        toolbar = tk.Frame(self.tab_code, bg=ProfessionalColors.SURFACE, height=48)
        toolbar.pack(fill="x", padx=16, pady=(16, 0))
        toolbar.pack_propagate(False)

        # 复制按钮
        copy_btn = ProfessionalButton(
            toolbar,
            text="复制代码",
            command=self.copy_code,
            variant="ghost",
            size="small"
        )
        copy_btn.pack(side="right", padx=(8, 0))

        # 保存按钮
        save_btn = ProfessionalButton(
            toolbar,
            text="保存文件",
            command=self.save_code,
            variant="ghost",
            size="small"
        )
        save_btn.pack(side="right", padx=(8, 0))

        # 刷新按钮
        refresh_btn = ProfessionalButton(
            toolbar,
            text="刷新预览",
            command=self.refresh_code_preview,
            variant="ghost",
            size="small"
        )
        refresh_btn.pack(side="right")

        # 代码编辑区域
        code_frame = tk.Frame(self.tab_code, bg=ProfessionalColors.CODE_BACKGROUND)
        code_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # 创建代码文本框
        self.code_text = scrolledtext.ScrolledText(
            code_frame,
            font=("Consolas", 11),
            bg=ProfessionalColors.CODE_BACKGROUND,
            fg=ProfessionalColors.CODE_TEXT,
            relief="flat",
            borderwidth=0,
            wrap="none",
            tabs=(4, 'left'),
            insertbackground=ProfessionalColors.CODE_TEXT
        )
        self.code_text.pack(fill="both", expand=True)

        # 设置初始代码
        sample_code = self._get_sample_rapid_code()
        self.code_text.insert("1.0", sample_code)

        # 配置语法高亮（简化版）
        self._configure_code_syntax()

    def _configure_code_syntax(self):
        """配置代码语法高亮"""
        # 关键词列表
        keywords = ['MODULE', 'PROC', 'CONST', 'VAR', 'IF', 'THEN', 'ELSE',
                    'ENDIF', 'FOR', 'TO', 'DO', 'ENDFOR', 'WHILE', 'ENDWHILE',
                    'RETURN', 'ENDPROC', 'ENDMODULE', 'MoveL', 'MoveJ', 'MoveC',
                    'TPWrite', 'WaitTime', 'SetDO', 'WaitDI', 'Stop']

        # 注释颜色
        self.code_text.tag_config("comment", foreground=ProfessionalColors.CODE_COMMENT)

        # 关键词颜色
        self.code_text.tag_config("keyword", foreground=ProfessionalColors.CODE_KEYWORD, font=("Consolas", 11, "bold"))

        # 字符串颜色
        self.code_text.tag_config("string", foreground=ProfessionalColors.CODE_STRING)

        # 数字颜色
        self.code_text.tag_config("number", foreground=ProfessionalColors.CODE_NUMBER)

    def _create_tab_model_info(self):
        """创建模型信息选项卡"""
        self.tab_model = tk.Frame(self.tab_control, bg=ProfessionalColors.BACKGROUND)
        self.tab_control.add(self.tab_model, text="模型信息")

        # 信息显示区域
        info_frame = tk.Frame(self.tab_model, bg=ProfessionalColors.BACKGROUND)
        info_frame.pack(fill="both", expand=True, padx=16, pady=16)

        # 详细信息文本框
        self.model_detail_text = scrolledtext.ScrolledText(
            info_frame,
            font=("微软雅黑", 10),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_PRIMARY,
            wrap="word",
            relief="flat",
            borderwidth=1
        )
        self.model_detail_text.pack(fill="both", expand=True)

        # 设置初始文本
        self.model_detail_text.insert("1.0",
                                      "模型详细信息将在此显示\n\n"
                                      "包括：\n"
                                      "• 文件信息和元数据\n"
                                      "• 几何特征分析\n"
                                      "• 网格质量评估\n"
                                      "• 数学建模参数\n"
                                      "• 处理状态和日志\n"
                                      )
        self.model_detail_text.configure(state="disabled")

    def _create_tab_path_preview(self):
        """创建路径预览选项卡"""
        self.tab_path = tk.Frame(self.tab_control, bg=ProfessionalColors.BACKGROUND)
        self.tab_control.add(self.tab_path, text="路径预览")

        # 路径信息区域
        path_frame = tk.Frame(self.tab_path, bg=ProfessionalColors.BACKGROUND)
        path_frame.pack(fill="both", expand=True, padx=16, pady=16)

        # 路径详细信息文本框
        self.path_detail_text = scrolledtext.ScrolledText(
            path_frame,
            font=("微软雅黑", 10),
            bg=ProfessionalColors.SURFACE,
            fg=ProfessionalColors.TEXT_PRIMARY,
            wrap="word",
            relief="flat",
            borderwidth=1
        )
        self.path_detail_text.pack(fill="both", expand=True)

        # 设置初始文本
        self.path_detail_text.insert("1.0",
                                     "抛光路径信息将在此显示\n\n"
                                     "包括：\n"
                                     "• 路径规划参数\n"
                                     "• 路径点详细信息\n"
                                     "• 加工时间估算\n"
                                     "• 碰撞检测结果\n"
                                     "• 优化建议\n"
                                     )
        self.path_detail_text.configure(state="disabled")

    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = tk.Frame(
            self.main_container,
            bg=ProfessionalColors.SURFACE_DARK,
            height=36
        )
        self.status_bar.pack(fill="x", side="bottom", pady=(16, 0))
        self.status_bar.pack_propagate(False)

        # 左侧状态信息
        self.status_label = tk.Label(
            self.status_bar,
            text="就绪 | ABB Polishing Studio 专业版",
            font=("微软雅黑", 9),
            bg=ProfessionalColors.SURFACE_DARK,
            fg=ProfessionalColors.TEXT_TERTIARY,
            padx=16
        )
        self.status_label.pack(side="left")

        # 中间进度信息
        self.progress_frame = tk.Frame(self.status_bar, bg=ProfessionalColors.SURFACE_DARK)
        self.progress_frame.pack(side="left", fill="x", expand=True)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            mode='determinate',
            length=200
        )
        self.progress_bar.pack(padx=16)

        # 右侧系统信息
        info_frame = tk.Frame(self.status_bar, bg=ProfessionalColors.SURFACE_DARK)
        info_frame.pack(side="right", padx=16)

        # 时间显示
        self.time_label = tk.Label(
            info_frame,
            text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            font=("微软雅黑", 8),
            bg=ProfessionalColors.SURFACE_DARK,
            fg=ProfessionalColors.TEXT_LIGHT
        )
        self.time_label.pack()

        # 更新时间显示
        self._update_time()

    def _update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self._update_time)

    def _bind_events(self):
        """绑定事件"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 绑定快捷键
        self.root.bind("<Control-o>", lambda e: self.browse_file())
        self.root.bind("<Control-s>", lambda e: self.save_code())
        self.root.bind("<Control-g>", lambda e: self.generate_code())
        self.root.bind("<F1>", lambda e: self.show_help())

    def _get_sample_rapid_code(self):
        """获取示例RAPID代码"""
        return """MODULE Polishing_Program
! ========================================================
! ABB Polishing Studio - 专业版 v8.1
! 基于NX几何特征的智能抛光程序
! ========================================================

! 工具数据定义
CONST tooldata tPolishingTool := [
    TRUE,
    [[0, 0, 100.0], [1, 0, 0, 0]],
    [0.500,
     [0, 0, 45.0],
     [1, 0, 0, 0],
     0.001, 0.001, 0.001]
];

! 主程序
PROC main()
    TPWrite "开始抛光程序";

    ! 执行粗抛
    Polishing_Rough();

    ! 执行精抛
    Polishing_Fine();

    TPWrite "抛光完成";
ENDPROC

! 粗抛子程序
PROC Polishing_Rough()
    TPWrite "开始粗抛";

    ! 抛光路径代码...

    TPWrite "粗抛完成";
ENDPROC

! 精抛子程序
PROC Polishing_Fine()
    TPWrite "开始精抛";

    ! 抛光路径代码...

    TPWrite "精抛完成";
ENDPROC

ENDMODULE"""

    # ==================== 主功能方法 ====================

    def browse_file(self):
        """浏览文件"""
        file_path = filedialog.askopenfilename(
            title="选择STL文件",
            filetypes=AppConfig.SUPPORTED_FORMATS
        )
        if file_path:
            self.file_path_var.set(file_path)

    def load_model(self):
        """加载模型"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("警告", "请先选择STL文件")
            return

        # 更新状态
        self.status_label.config(text="正在加载模型...")
        self.progress_var.set(30)
        self.root.update()

        try:
            # 加载模型逻辑
            # 这里调用之前定义的加载函数
            self.current_model = self.nx_processor.load_stl_with_metadata(
                file_path,
                force_nx_processing=self.nx_processing_var.get()
            )

            if self.current_model:
                self.model_metadata = self.current_model.metadata

                # 更新UI
                info_text = f"✅ 模型加载成功!\n\n"
                info_text += f"文件: {os.path.basename(file_path)}\n"
                info_text += f"顶点数: {len(self.current_model.vertices):,}\n"
                info_text += f"面片数: {len(self.current_model.faces):,}\n"

                self.model_info_text.configure(state="normal")
                self.model_info_text.delete("1.0", tk.END)
                self.model_info_text.insert("1.0", info_text)
                self.model_info_text.configure(state="disabled")

                # 更新模型状态
                self.model_status_icon.config(text="●", fg=self.colors.SUCCESS)
                self.model_status_text.config(text=f"已加载: {os.path.basename(file_path)}")

                self.status_label.config(text="模型加载完成")
                self.progress_var.set(100)

                messagebox.showinfo("成功", "模型加载完成")
            else:
                raise Exception("模型加载失败")

        except Exception as e:
            messagebox.showerror("错误", f"加载模型失败:\n{str(e)}")
            self.status_label.config(text="加载失败")
            self.progress_var.set(0)

    def generate_paths(self):
        """生成抛光路径"""
        if not self.current_model:
            messagebox.showwarning("警告", "请先加载模型")
            return

        # 更新状态
        self.status_label.config(text="正在生成路径...")
        self.progress_var.set(30)
        self.root.update()

        try:
            # 路径生成逻辑
            # 这里调用之前定义的路径生成函数

            # 模拟路径数据
            simulated_paths = self._generate_simulated_paths()
            self.paths = simulated_paths

            # 更新UI
            info_text = f"✅ 路径生成完成!\n\n"
            info_text += f"类型: {self.path_type_var.get()}\n"
            info_text += f"粗抛路径: {len(simulated_paths.get('rough', []))} 条\n"
            info_text += f"精抛路径: {len(simulated_paths.get('fine', []))} 条\n"
            info_text += f"总点数: {self._count_total_points(simulated_paths)}\n"

            self.path_info_text.configure(state="normal")
            self.path_info_text.delete("1.0", tk.END)
            self.path_info_text.insert("1.0", info_text)
            self.path_info_text.configure(state="disabled")

            self.status_label.config(text="路径生成完成")
            self.progress_var.set(100)

            messagebox.showinfo("成功", "抛光路径生成完成")

        except Exception as e:
            messagebox.showerror("错误", f"生成路径失败:\n{str(e)}")
            self.status_label.config(text="路径生成失败")
            self.progress_var.set(0)

    def _generate_simulated_paths(self):
        """生成模拟路径数据"""
        # 模拟路径生成
        rough_paths = []
        fine_paths = []

        # 粗抛路径
        for i in range(3):
            points = []
            for j in range(10):
                points.append({
                    'position': [i * 50 + j * 5, i * 30 + j * 3, 100 + j * 2],
                    'orientation': [1.0, 0.0, 0.0, 0.0]
                })
            rough_paths.append({
                'id': i,
                'name': f'粗抛路径_{i + 1}',
                'points': points
            })

        # 精抛路径
        for i in range(2):
            points = []
            for j in range(15):
                points.append({
                    'position': [i * 30 + j * 3, i * 20 + j * 2, 100 + j * 1],
                    'orientation': [1.0, 0.0, 0.0, 0.0]
                })
            fine_paths.append({
                'id': i,
                'name': f'精抛路径_{i + 1}',
                'points': points
            })

        return {'rough': rough_paths, 'fine': fine_paths}

    def _count_total_points(self, paths):
        """计算总路径点数"""
        total = 0
        for stage in ['rough', 'fine']:
            if stage in paths:
                for path in paths[stage]:
                    total += len(path.get('points', []))
        return total

    def generate_code(self):
        """生成RAPID代码"""
        if not self.paths:
            messagebox.showwarning("警告", "请先生成抛光路径")
            return

        # 更新状态
        self.status_label.config(text="正在生成代码...")
        self.progress_var.set(30)
        self.root.update()

        try:
            # 准备数据
            program_data = {
                'program_name': self.program_name_var.get(),
                'robot_model': self.robot_model_var.get(),
                'tool_name': 'tPolishingTool',
                'tool_diameter': self.tool_diameter_var.get(),
                'tool_length': self.tool_length_var.get(),
                'workpiece_name': 'Workpiece',
                'rough_speed': 300,
                'fine_speed': 200,
                'paths': self.paths,
                'include_io': self.include_io_var.get(),
                'include_safety': self.include_safety_var.get()
            }

            # 生成代码
            self.generated_code = self.rapid_generator.generate_complete_program(program_data)

            # 显示代码
            self.code_text.delete("1.0", tk.END)
            self.code_text.insert("1.0", self.generated_code)

            # 应用语法高亮
            self._apply_syntax_highlighting()

            self.status_label.config(text="代码生成完成")
            self.progress_var.set(100)

            messagebox.showinfo("成功", "RAPID代码生成完成")

        except Exception as e:
            messagebox.showerror("错误", f"生成代码失败:\n{str(e)}")
            self.status_label.config(text="代码生成失败")
            self.progress_var.set(0)

    def _apply_syntax_highlighting(self):
        """应用语法高亮"""
        # 清除现有标记
        for tag in self.code_text.tag_names():
            if tag not in ["sel", "comment", "keyword", "string", "number"]:
                self.code_text.tag_remove(tag, "1.0", tk.END)

        # 高亮注释
        self.code_text.tag_add("comment", "1.0", tk.END)

        # 高亮关键词（简化实现）
        keywords = ['MODULE', 'PROC', 'CONST', 'VAR', 'IF', 'THEN', 'ELSE',
                    'ENDIF', 'FOR', 'TO', 'DO', 'ENDFOR', 'MoveL', 'MoveJ',
                    'TPWrite', 'WaitTime', 'SetDO', 'WaitDI', 'Stop']

        content = self.code_text.get("1.0", tk.END)
        for keyword in keywords:
            start = "1.0"
            while True:
                start = self.code_text.search(r'\b' + keyword + r'\b', start, tk.END,
                                              regexp=True, nocase=True)
                if not start:
                    break
                end = f"{start}+{len(keyword)}c"
                self.code_text.tag_add("keyword", start, end)
                start = end

    def export_program(self):
        """导出程序"""
        if not self.generated_code:
            messagebox.showwarning("警告", "请先生成RAPID代码")
            return

        # 选择保存位置
        default_name = f"{self.program_name_var.get()}.mod"
        file_path = filedialog.asksaveasfilename(
            title="保存RAPID程序",
            defaultextension=".mod",
            initialfile=default_name,
            filetypes=[
                ("ABB RAPID程序", "*.mod"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )

        if not file_path:
            return

        # 更新状态
        self.status_label.config(text="正在导出程序...")
        self.progress_var.set(50)
        self.root.update()

        try:
            # 导出程序
            success = self.rapid_generator.export_program(self.generated_code, file_path)

            if success:
                self.status_label.config(text="程序导出成功")
                self.progress_var.set(100)
                messagebox.showinfo("成功", f"程序已导出到:\n{file_path}")
            else:
                messagebox.showerror("错误", "导出失败")
                self.status_label.config(text="导出失败")
                self.progress_var.set(0)

        except Exception as e:
            messagebox.showerror("错误", f"导出失败:\n{str(e)}")
            self.status_label.config(text="导出失败")
            self.progress_var.set(0)

    def copy_code(self):
        """复制代码"""
        if not self.generated_code:
            messagebox.showwarning("警告", "没有可复制的代码")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(self.generated_code)
        self.status_label.config(text="代码已复制到剪贴板")

    def save_code(self):
        """保存代码"""
        self.export_program()

    def refresh_code_preview(self):
        """刷新代码预览"""
        self.code_text.delete("1.0", tk.END)
        if self.generated_code:
            self.code_text.insert("1.0", self.generated_code)
            self._apply_syntax_highlighting()
        else:
            self.code_text.insert("1.0", self._get_sample_rapid_code())

    def execute_full_process(self):
        """执行完整流程"""
        steps = [
            ("加载模型", self.load_model),
            ("生成路径", self.generate_paths),
            ("生成代码", self.generate_code),
            ("导出程序", self.export_program)
        ]

        for step_name, step_func in steps:
            try:
                self.status_label.config(text=f"正在执行: {step_name}")
                self.progress_var.set(0)
                self.root.update()

                # 执行步骤
                step_func()

                # 短暂暂停
                time.sleep(0.5)

            except Exception as e:
                messagebox.showerror("流程中断", f"{step_name}失败:\n{str(e)}")
                return

        messagebox.showinfo("完成", "完整流程执行完成！")

    def show_help(self):
        """显示帮助"""
        help_text = """
ABB Polishing Studio 专业版 - 使用帮助

基本流程:
1. 选择并加载STL模型文件
2. 配置机器人和工具参数
3. 生成抛光路径
4. 生成并导出RAPID程序

快捷键:
Ctrl+O - 打开文件
Ctrl+S - 保存程序
Ctrl+G - 生成代码
F1 - 显示帮助

支持功能:
• NX STL文件特殊处理
• 自适应路径规划
• 工业级RAPID代码生成
• 3D模型预览
• 数学建模优化
        """
        messagebox.showinfo("帮助", help_text)

    def on_closing(self):
        """关闭应用程序"""
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.root.destroy()

    def run(self):
        """运行应用程序"""
        try:
            print("=" * 80)
            print(f"{AppConfig.APP_NAME} - {AppConfig.VERSION}")
            print("专业版 - UI优化配色方案")
            print("=" * 80)
            self.root.mainloop()
        except Exception as e:
            print(f"应用程序运行错误: {e}")


# ==================== 数学建模模块 ====================
class PolishingMathematicalModel:
    """抛光数学建模类"""

    @staticmethod
    def calculate_surface_curvature(mesh, k_neighbors=10):
        """计算表面曲率"""
        vertices = mesh.vertices
        curvatures = []

        # 构建KD树用于快速查找邻居
        tree = cKDTree(vertices)

        for i, point in enumerate(vertices):
            # 查找最近邻点
            distances, indices = tree.query(point, k=k_neighbors + 1)
            neighbors = vertices[indices[1:]]  # 排除自身

            # 计算PCA
            if len(neighbors) >= 3:
                centered = neighbors - neighbors.mean(axis=0)
                cov_matrix = centered.T @ centered
                eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

                # 特征值排序（升序）
                sorted_indices = np.argsort(eigenvalues)
                eigenvalues = eigenvalues[sorted_indices]

                # 计算曲率
                if eigenvalues[2] > 0:
                    curvature = eigenvalues[0] / eigenvalues[2]
                    curvatures.append(curvature)
                else:
                    curvatures.append(0)
            else:
                curvatures.append(0)

        return np.array(curvatures)

    @staticmethod
    def calculate_surface_normals(mesh):
        """计算表面法向量"""
        if hasattr(mesh, 'face_normals') and len(mesh.face_normals) > 0:
            return mesh.face_normals
        else:
            # 手动计算法向量
            vertices = mesh.vertices
            faces = mesh.faces

            normals = np.zeros((len(faces), 3))
            for i, face in enumerate(faces):
                v1 = vertices[face[1]] - vertices[face[0]]
                v2 = vertices[face[2]] - vertices[face[0]]
                normal = np.cross(v1, v2)
                normal_length = np.linalg.norm(normal)
                if normal_length > 0:
                    normals[i] = normal / normal_length

            return normals

    @staticmethod
    def calculate_contact_pressure(tool_radius, force, curvature):
        """计算接触压力分布"""
        # Hertz接触理论简化模型
        if curvature <= 0:
            return force / (np.pi * tool_radius ** 2)

        effective_radius = 1 / curvature if curvature != 0 else tool_radius
        contact_radius = np.cbrt(3 * force * effective_radius / (4 * 210e9))  # 假设弹性模量210GPa

        max_pressure = 1.5 * force / (np.pi * contact_radius ** 2)
        return max_pressure

    @staticmethod
    def calculate_material_removal_rate(pressure, speed, tool_radius, material_coeff=1e-8):
        """计算材料去除率"""
        # Preston方程: MRR = k * P * v
        # k: 材料系数, P: 压力, v: 相对速度
        contact_area = np.pi * tool_radius ** 2
        return material_coeff * pressure * speed * contact_area

    @staticmethod
    def optimize_path_length(points):
        """优化路径长度（旅行商问题简化版）"""
        if len(points) <= 2:
            return points

        # 使用最近邻算法优化路径
        current_idx = 0
        visited = [False] * len(points)
        visited[current_idx] = True
        optimized_path = [points[current_idx]]

        for _ in range(len(points) - 1):
            min_dist = float('inf')
            next_idx = -1

            for i, point in enumerate(points):
                if not visited[i]:
                    dist = np.linalg.norm(points[current_idx] - point)
                    if dist < min_dist:
                        min_dist = dist
                        next_idx = i

            if next_idx != -1:
                visited[next_idx] = True
                optimized_path.append(points[next_idx])
                current_idx = next_idx

        return np.array(optimized_path)

    @staticmethod
    def calculate_tool_orientation(normal, approach_angle=45):
        """计算工具姿态（四元数）"""
        # 将法向量转换为四元数
        normal = normal / np.linalg.norm(normal)

        # 计算旋转轴和角度
        up_vector = np.array([0, 0, 1])
        if np.allclose(normal, up_vector) or np.allclose(normal, -up_vector):
            axis = np.array([1, 0, 0])
        else:
            axis = np.cross(up_vector, normal)
            axis = axis / np.linalg.norm(axis)

        # 计算旋转角度
        angle = np.arccos(np.clip(np.dot(up_vector, normal), -1.0, 1.0))

        # 转换为四元数
        qw = np.cos(angle / 2)
        qx = axis[0] * np.sin(angle / 2)
        qy = axis[1] * np.sin(angle / 2)
        qz = axis[2] * np.sin(angle / 2)

        return [qw, qx, qy, qz]

    @staticmethod
    def generate_spiral_path(center, radius, start_height, end_height, points_per_revolution=20, revolutions=5):
        """生成螺旋路径"""
        points = []

        for i in range(revolutions * points_per_revolution):
            angle = 2 * np.pi * i / points_per_revolution
            r = radius * (revolutions * points_per_revolution - i) / (revolutions * points_per_revolution)

            x = center[0] + r * np.cos(angle)
            y = center[1] + r * np.sin(angle)
            z = start_height + (end_height - start_height) * i / (revolutions * points_per_revolution)

            points.append([x, y, z])

        return np.array(points)

    @staticmethod
    def calculate_force_distribution(tool_path, surface_normals, desired_force=30.0):
        """计算力分布"""
        force_distribution = []

        for i, normal in enumerate(surface_normals):
            # 根据曲率和表面特性调整力
            if i < len(tool_path):
                curvature = np.random.random() * 0.01  # 简化
                adjusted_force = desired_force * (1 + 0.5 * curvature)
                force_distribution.append(min(adjusted_force, 50.0))  # 限制最大力

        return np.array(force_distribution)

    @staticmethod
    def smooth_path(points, smoothing_factor=0.5):
        """平滑路径"""
        if len(points) < 3:
            return points

        smoothed = np.copy(points)
        for i in range(1, len(points) - 1):
            smoothed[i] = (points[i - 1] + points[i] * 2 + points[i + 1]) / 4

        return smoothed

    @staticmethod
    def calculate_energy_consumption(path_length, force, speed, efficiency=0.8):
        """计算能量消耗"""
        # E = F * d / η
        return force * path_length / efficiency


# ==================== 高级路径规划算法 ====================
class AdvancedPathPlanner:
    """高级路径规划算法"""

    def __init__(self, mesh, tool_radius=8.0):
        self.mesh = mesh
        self.tool_radius = tool_radius
        self.vertices = mesh.vertices
        self.faces = mesh.faces

    def generate_adaptive_path(self, stepover_ratio=0.5):
        """生成自适应路径"""
        # 计算曲率
        curvatures = PolishingMathematicalModel.calculate_surface_curvature(self.mesh)

        # 获取边界框
        min_coords = np.min(self.vertices, axis=0)
        max_coords = np.max(self.vertices, axis=0)

        # 生成路径点
        paths = []
        step_size = self.tool_radius * stepover_ratio

        # 根据曲率调整步距
        for z in np.arange(min_coords[2], max_coords[2], step_size):
            layer_points = []

            # 找到当前Z层的点
            mask = (self.vertices[:, 2] >= z) & (self.vertices[:, 2] < z + step_size)
            if np.any(mask):
                layer_vertices = self.vertices[mask]
                layer_curvatures = curvatures[mask]

                # 根据曲率排序
                sorted_indices = np.argsort(layer_curvatures)
                sorted_points = layer_vertices[sorted_indices]

                # 优化路径
                optimized = PolishingMathematicalModel.optimize_path_length(sorted_points)
                layer_points = optimized.tolist()

            if layer_points:
                paths.append({
                    'points': layer_points,
                    'z_level': z,
                    'step_size': step_size
                })

        return paths

    def generate_parallel_path(self, angle=0, spacing=None):
        """生成平行线路径"""
        if spacing is None:
            spacing = self.tool_radius * 0.7

        # 获取边界框
        min_coords = np.min(self.vertices, axis=0)
        max_coords = np.max(self.vertices, axis=0)

        paths = []

        # 生成平行线
        if angle == 0:  # X方向
            for y in np.arange(min_coords[1], max_coords[1], spacing):
                line_points = []
                for x in np.arange(min_coords[0], max_coords[0], spacing):
                    # 找到最近的表面点
                    distances = np.sqrt((self.vertices[:, 0] - x) ** 2 + (self.vertices[:, 1] - y) ** 2)
                    closest_idx = np.argmin(distances)
                    if distances[closest_idx] < spacing:
                        point = self.vertices[closest_idx].tolist()
                        line_points.append(point)

                if line_points:
                    paths.append({'points': line_points, 'direction': 'x'})

        elif angle == 90:  # Y方向
            for x in np.arange(min_coords[0], max_coords[0], spacing):
                line_points = []
                for y in np.arange(min_coords[1], max_coords[1], spacing):
                    distances = np.sqrt((self.vertices[:, 0] - x) ** 2 + (self.vertices[:, 1] - y) ** 2)
                    closest_idx = np.argmin(distances)
                    if distances[closest_idx] < spacing:
                        point = self.vertices[closest_idx].tolist()
                        line_points.append(point)

                if line_points:
                    paths.append({'points': line_points, 'direction': 'y'})

        return paths

    def generate_spiral_path(self, center=None, max_radius=None):
        """生成螺旋路径"""
        if center is None:
            center = np.mean(self.vertices, axis=0)

        if max_radius is None:
            distances = np.sqrt(np.sum((self.vertices[:, :2] - center[:2]) ** 2, axis=1))
            max_radius = np.max(distances)

        # 生成螺旋路径点
        spiral_points = PolishingMathematicalModel.generate_spiral_path(
            center[:2], max_radius,
            np.min(self.vertices[:, 2]),
            np.max(self.vertices[:, 2])
        )

        # 投影到表面
        surface_points = []
        tree = cKDTree(self.vertices)

        for point in spiral_points:
            distances, indices = tree.query(point, k=3)
            # 加权平均
            weights = 1 / (distances + 1e-6)
            weights = weights / np.sum(weights)
            surface_point = np.sum(self.vertices[indices] * weights.reshape(-1, 1), axis=0)
            surface_points.append(surface_point.tolist())

        return [{'points': surface_points, 'type': 'spiral'}]

    def calculate_path_coverage(self, paths):
        """计算路径覆盖率"""
        if not paths or not hasattr(self, 'vertices'):
            return 0.0

        # 简化计算：检查有多少顶点在工具半径范围内
        covered_count = 0
        tool_influence_radius = self.tool_radius * 1.5

        for vertex in self.vertices:
            covered = False

            for path in paths:
                for point in path.get('points', []):
                    distance = np.linalg.norm(vertex - np.array(point))
                    if distance < tool_influence_radius:
                        covered = True
                        break
                if covered:
                    break

            if covered:
                covered_count += 1

        return covered_count / len(self.vertices) if len(self.vertices) > 0 else 0.0

    def optimize_path_sequence(self, paths, start_point=None):
        """优化路径序列"""
        if not paths:
            return paths

        if start_point is None:
            start_point = np.mean(self.vertices, axis=0)

        # 计算每条路径的起点
        path_starts = []
        for i, path in enumerate(paths):
            if path.get('points'):
                path_starts.append((i, path['points'][0]))

        # 使用最近邻算法优化顺序
        optimized_order = []
        visited = [False] * len(path_starts)
        current_pos = start_point

        for _ in range(len(path_starts)):
            min_dist = float('inf')
            next_idx = -1

            for i, (path_idx, start_pos) in enumerate(path_starts):
                if not visited[i]:
                    distance = np.linalg.norm(current_pos - np.array(start_pos))
                    if distance < min_dist:
                        min_dist = distance
                        next_idx = i

            if next_idx != -1:
                visited[next_idx] = True
                optimized_order.append(path_starts[next_idx][0])
                current_pos = np.array(path_starts[next_idx][1])

        # 重新排序路径
        return [paths[i] for i in optimized_order]


# ==================== NX STL专业处理库 ====================
class NXSTLProcessor:
    """NX STL文件专业处理器"""

    # NX特定参数和标志
    NX_MAGIC_NUMBERS = {
        'HEADER': b'NX STL',
        'VERSION': b'V2.0',
        'UNITS': {
            b'MM': '毫米',
            b'IN': '英寸',
            b'M': '米'
        }
    }

    @staticmethod
    def is_nx_stl(file_path):
        """检查是否为NX生成的STL文件"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(80)
                # NX STL通常有特殊标识，但不同版本可能有不同
                header_str = header.decode('ascii', errors='ignore')

                # 更宽松的检查：NX标识可能在不同位置
                # 1. 直接检查NX/Siemens/UG
                if any(keyword in header_str for keyword in ['NX', 'Siemens', 'UG', 'Unigraphics']):
                    return True

                # 2. 检查常见的NX格式特征
                # NX生成的STL通常有特定的格式模式
                lines = header_str.strip().split('\n')
                for line in lines:
                    if any(marker in line for marker in ['UNITS=', 'Units=', 'CREATED=', 'Created=']):
                        return True

                # 3. 如果是二进制STL，检查面片数
                # 二进制STL: 80字节头 + 4字节面片数
                f.seek(0)
                full_header = f.read(84)
                if len(full_header) == 84:
                    # 检查是否有合理的面片数（小端存储）
                    face_count = struct.unpack('<I', full_header[80:84])[0]
                    # 如果面片数为0，可能不是有效的STL
                    if face_count == 0:
                        return False
                    # 尝试读取一些面片来验证
                    # 每个面片: 12字节法向量 + 36字节顶点 + 2字节属性
                    face_size = 50
                    expected_file_size = 84 + face_count * face_size
                    actual_file_size = os.path.getsize(file_path)

                    # 允许一定的误差（属性字节可能不同）
                    if abs(expected_file_size - actual_file_size) <= 2:
                        # 可能是有效的STL，但不是NX特定的
                        return False

                return False
        except Exception as e:
            print(f"检查NX STL时出错: {e}")
            return False

    @staticmethod
    def read_nx_stl_metadata(file_path):
        """读取NX STL文件的元数据"""
        metadata = {
            'is_nx': False,
            'units': '毫米',
            'version': '未知',
            'creation_date': None,
            'author': None,
            'part_name': None,
            'original_format': 'STL',
            'nx_specific': {},
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
        }

        try:
            with open(file_path, 'rb') as f:
                # 读取头信息
                header = f.read(84)  # 80字节头 + 4字节面片数

                # 解析头信息
                header_str = header[:80].decode('ascii', errors='ignore')

                # 检查是否是二进制STL
                is_binary = False
                if len(header) == 84:
                    try:
                        face_count = struct.unpack('<I', header[80:84])[0]
                        # 如果是二进制STL，重置文件指针
                        f.seek(84)  # 移动到数据开始处
                        is_binary = True
                        metadata['format'] = 'Binary STL'
                        metadata['face_count'] = face_count
                    except:
                        metadata['format'] = 'ASCII STL'

                # 更智能地检测NX文件
                nx_indicators = ['NX', 'Siemens', 'UG', 'Unigraphics']
                has_nx_indicator = any(indicator in header_str for indicator in nx_indicators)

                # 检查特定的NX元数据格式
                has_nx_metadata = False
                nx_metadata_patterns = [
                    r'UNITS\s*=\s*[A-Z]+',
                    r'CREATED\s*=\s*[0-9\-]+',
                    r'PART\s*=\s*.+',
                    r'Part\s*=\s*.+'
                ]

                for pattern in nx_metadata_patterns:
                    if re.search(pattern, header_str, re.IGNORECASE):
                        has_nx_metadata = True
                        break

                # 如果是NX文件或具有NX特征
                if has_nx_indicator or has_nx_metadata:
                    metadata['is_nx'] = True
                    metadata['original_format'] = 'NX STL'

                    # 提取可能的NX信息
                    lines = header_str.split('\n')
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue

                        # 单位信息
                        if 'UNITS=' in line.upper() or 'Units=' in line:
                            if 'MM' in line.upper():
                                metadata['units'] = '毫米'
                            elif 'IN' in line.upper():
                                metadata['units'] = '英寸'
                            elif 'M' in line.upper():
                                metadata['units'] = '米'
                            elif 'CM' in line.upper():
                                metadata['units'] = '厘米'

                        # 创建日期
                        elif 'CREATED=' in line.upper() or 'Created=' in line:
                            date_match = re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', line)
                            if date_match:
                                metadata['creation_date'] = date_match.group()

                        # 零件名称
                        elif 'PART=' in line.upper() or 'Part=' in line:
                            part_match = re.search(r'[Pp]art[:=]\s*(.+)', line)
                            if part_match:
                                metadata['part_name'] = part_match.group(1).strip()
                            else:
                                # 尝试直接提取等号后的内容
                                parts = line.split('=')
                                if len(parts) > 1:
                                    metadata['part_name'] = parts[1].strip()

                        # 作者信息
                        elif 'AUTHOR=' in line.upper() or 'Author=' in line:
                            author_match = re.search(r'[Aa]uthor[:=]\s*(.+)', line)
                            if author_match:
                                metadata['author'] = author_match.group(1).strip()

                        # 版本信息
                        elif 'VERSION=' in line.upper() or 'Version=' in line:
                            version_match = re.search(r'[Vv]ersion[:=]\s*(.+)', line)
                            if version_match:
                                metadata['version'] = version_match.group(1).strip()

                        # 公差信息
                        elif 'TOLERANCE=' in line.upper() or 'Tolerance=' in line:
                            tol_match = re.search(r'[Tt]olerance[:=]\s*([0-9.]+)', line)
                            if tol_match:
                                metadata['nx_specific']['tolerance'] = float(tol_match.group(1))

                # 如果没有检测到NX特征，尝试其他CAD格式
                else:
                    # 检查其他CAD系统的特征
                    other_cad_indicators = {
                        'SolidWorks': ['SolidWorks', 'SW'],
                        'CATIA': ['CATIA', 'V5'],
                        'Pro/ENGINEER': ['Pro/ENGINEER', 'CREO', 'PTC'],
                        'AutoCAD': ['AutoCAD', 'ACAD'],
                        'Inventor': ['Inventor'],
                        'Fusion 360': ['Fusion']
                    }

                    for cad_name, indicators in other_cad_indicators.items():
                        if any(indicator in header_str for indicator in indicators):
                            metadata['original_format'] = f'{cad_name} STL'
                            metadata['cad_system'] = cad_name
                            break

            return metadata
        except Exception as e:
            print(f"读取STL元数据失败: {e}")
            # 返回基本元数据
            metadata['original_format'] = 'Unknown STL'
            return metadata

    @staticmethod
    def load_stl_with_metadata(file_path, force_nx_processing=False):
        """加载STL文件并尝试提取元数据"""
        try:
            if not TRIMESH_AVAILABLE:
                raise ImportError("需要安装trimesh库")

            # 读取元数据
            metadata = NXSTLProcessor.read_nx_stl_metadata(file_path)

            # 使用trimesh加载模型
            mesh = trimesh.load(file_path)

            # 添加元数据到网格属性
            if hasattr(mesh, 'metadata'):
                mesh.metadata.update(metadata)
            else:
                mesh.metadata = metadata

            # 如果用户强制使用NX处理或检测到是NX文件
            if force_nx_processing or metadata.get('is_nx', False):
                # 单位转换检查
                if metadata['units'] == '英寸':
                    # 英寸转毫米
                    mesh.vertices *= 25.4
                    print("已将英寸单位转换为毫米")
                elif metadata['units'] == '米':
                    # 米转毫米
                    mesh.vertices *= 1000
                    print("已将米单位转换为毫米")
                elif metadata['units'] == '厘米':
                    # 厘米转毫米
                    mesh.vertices *= 10
                    print("已将厘米单位转换为毫米")

            return mesh
        except Exception as e:
            print(f"加载STL文件失败: {e}")
            # 尝试基本的加载方式
            try:
                mesh = trimesh.load(file_path)
                mesh.metadata = {
                    'is_nx': False,
                    'units': '毫米',
                    'original_format': 'Basic STL',
                    'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
                }
                return mesh
            except Exception as e2:
                print(f"基本加载也失败: {e2}")
                return None

    @staticmethod
    def analyze_mesh_features(mesh):
        """分析网格特征"""
        if mesh is None:
            return {}

        features = {
            'triangle_count': len(mesh.faces) if hasattr(mesh, 'faces') else 0,
            'vertex_count': len(mesh.vertices) if hasattr(mesh, 'vertices') else 0,
            'is_watertight': mesh.is_watertight if hasattr(mesh, 'is_watertight') else False,
            'is_closed': mesh.is_closed if hasattr(mesh, 'is_closed') else False,
            'is_convex': mesh.is_convex if hasattr(mesh, 'is_convex') else False,
            'bounding_box': None,
            'volume': None,
            'surface_area': None,
            'center_mass': None,
            'inertia': None
        }

        # 计算边界框
        if hasattr(mesh, 'vertices') and len(mesh.vertices) > 0:
            min_coords = np.min(mesh.vertices, axis=0)
            max_coords = np.max(mesh.vertices, axis=0)
            features['bounding_box'] = {
                'min': min_coords.tolist(),
                'max': max_coords.tolist(),
                'size': (max_coords - min_coords).tolist(),
                'center': ((min_coords + max_coords) / 2).tolist()
            }

        # 计算体积和表面积
        try:
            if hasattr(mesh, 'volume'):
                features['volume'] = mesh.volume
            if hasattr(mesh, 'area'):
                features['surface_area'] = mesh.area
            if hasattr(mesh, 'center_mass'):
                features['center_mass'] = mesh.center_mass.tolist()
            if hasattr(mesh, 'moment_inertia'):
                features['inertia'] = mesh.moment_inertia.tolist()
        except Exception as e:
            print(f"计算网格特征时出错: {e}")

        return features


# ==================== RAPID高级功能扩展 ====================
class AdvancedRAPIDFeatures:
    """RAPID高级功能扩展"""

    @staticmethod
    def generate_force_control_code(tool_data, force_params):
        """生成力控制代码"""
        return f"""! 力控制参数
CONST forcedata fPolishing := [
    1,
    [[0, 0, {force_params.get('compliance', 0.1)}], [1, 0, 0, 0]],
    {force_params.get('max_force', 50.0)},
    {force_params.get('max_force', 50.0)}
];

! 力控制程序
PROC ForcePolishing()
    ! 启用力控制
    SearchL \\Force, fPolishing, pStart, vApproach, tPolishingTool;

    ! 力控制抛光
    ForceL [[0, 0, {force_params.get('target_force', 30.0)}]], fPolishing, pPath, vRough, tPolishingTool;

    ! 禁用力控制
    StopForce;
ENDPROC"""

    @staticmethod
    def generate_synchronized_motion_code(axes_data):
        """生成同步运动代码"""
        return f"""! 同步运动控制
PROC SyncMotion()
    ! 定义外部轴
    VAR syncident syncExternal;

    ! 同步移动
    SyncMoveOn syncExternal, \\Tool:=tPolishingTool;

    ! 同步运动指令
    MoveL pTarget, vRough, zFine, tPolishingTool \\Conc;

    ! 结束同步
    SyncMoveOff syncExternal;
ENDPROC"""

    @staticmethod
    def generate_error_recovery_code():
        """生成错误恢复代码"""
        return """! 错误恢复程序
PROC ErrorRecovery()
    ! 保存当前位置
    VAR jointtarget jCurrent;
    jCurrent := CJointT();

    ! 错误处理
    TRYNEXT;
    IF ERRNO = ERR_HAND_HEAVY THEN
        ! 手动引导错误
        TPWrite "手动引导错误，恢复中...";
        MoveAbsJ jCurrent, vFast, fine, tPolishingTool;
    ELSEIF ERRNO = ERR_COLL_STOP THEN
        ! 碰撞停止错误
        TPWrite "碰撞检测，恢复中...";
        StopMove \\Quick;
        MoveAbsJ jCurrent, vSlow, fine, tPolishingTool;
    ELSE
        ! 其他错误
        TPWrite "未知错误，尝试恢复...";
        StopMove;
        MoveAbsJ jCurrent, vSlow, fine, tPolishingTool;
    ENDIF

    RETRY;
ENDPROC"""

    @staticmethod
    def generate_optimization_code(optimization_params):
        """生成优化代码"""
        return f"""! 运动优化参数
CONST optdata optPolishing := [
    [{optimization_params.get('acceleration', 0.8)},
     {optimization_params.get('jerk', 0.5)},
     {optimization_params.get('corner_radius', 10.0)}],
    [TRUE, TRUE, TRUE, TRUE, TRUE]
];

! 优化运动程序
PROC OptimizedMotion()
    ! 应用优化
    PathAccLim \\AccLim, {optimization_params.get('max_accel', 5000.0)}, {optimization_params.get('max_decel', 5000.0)};
    PathResol \\CirPathRes, {optimization_params.get('path_resolution', 1.0)};

    ! 平滑运动
    SingArea \\Wrist;
    ConfL \\Off;

    ! 执行优化运动
    MoveL pTarget, vRough \\T:=optPolishing, tPolishingTool;
ENDPROC"""

    @staticmethod
    def generate_advanced_polishing_cycle(stage, path_data, force_control=False, synchronization=False):
        """生成高级抛光循环"""
        code = f"""PROC AdvancedPolishing_{stage.capitalize()}()
    ! 高级{stage}抛光循环

    VAR num nPathIndex := 1;
    VAR num nForceSetpoint := {30 if stage == 'rough' else 20};
    VAR bool bForceControlActive := {force_control};

    ! 力控制初始化
    IF bForceControlActive THEN
        ForceDef fPolishing_{stage}, [[0, 0, nForceSetpoint]], tPolishingTool;
        ForceAct fPolishing_{stage};
    ENDIF"""

        if synchronization:
            code += """

    ! 同步运动初始化
    VAR syncident syncExternal;
    SyncMoveOn syncExternal, \\Tool:=tPolishingTool;"""

        code += f"""

    ! 主抛光循环
    FOR nPathIndex FROM 1 TO {len(path_data.get('points', []))} DO
        ! 移动到目标点
        MoveL IndPos(pPathStart, nPathIndex-1), v{stage.capitalize()}, zMedium, tPolishingTool \\WObj:=wWorkpiece;

        ! 力控制抛光
        IF bForceControlActive THEN
            ForceL [[0, 0, nForceSetpoint]], fPolishing_{stage}, v{stage.capitalize()}, tPolishingTool \\WObj:=wWorkpiece;
        ENDIF

        ! 等待抛光时间
        WaitTime 0.1;
    ENDFOR"""

        if synchronization:
            code += """

    ! 结束同步运动
    SyncMoveOff syncExternal;"""

        if force_control:
            code += """

    ! 禁用力控制
    StopForce;"""

        code += """

    TPWrite "高级抛光循环完成";
ENDPROC"""

        return code


# ==================== 工业级RAPID代码生成器 ====================
class IndustrialRAPIDGenerator:
    """工业级ABB RAPID代码生成器"""

    # RAPID语法模板
    RAPID_TEMPLATES = {
        'module_header': """MODULE {module_name}

! 生成时间: {timestamp}
""",

        'tool_data': """! 工具数据定义
CONST tooldata {tool_name} := [
    TRUE,
    [[0, 0, {tool_length:.1f}], [1, 0, 0, 0]],
    [{tool_mass:.3f},
     [0, 0, {tool_cg_z:.1f}],
     [1, 0, 0, 0],
     {inertia_ix:.3f}, {inertia_iy:.3f}, {inertia_iz:.3f}]
];""",

        'wobj_data': """! 工件坐标系定义
CONST wobjdata {wobj_name} := [
    FALSE,
    TRUE,
    "{wobj_uframe}",
    [[0, 0, 0], [1, 0, 0, 0]],
    [[{wobj_offset_x:.1f}, {wobj_offset_y:.1f}, {wobj_offset_z:.1f}],
     [{wobj_q1:.4f}, {wobj_q2:.4f}, {wobj_q3:.4f}, {wobj_q4:.4f}]]
];""",

        'speed_data': """! 速度数据定义
CONST speeddata vApproach := [100, 500, 5000, 1000];
CONST speeddata vRough := [{rough_speed}, 500, 5000, 1000];
CONST speeddata vFine := [{fine_speed}, 500, 5000, 1000];
CONST speeddata vRetract := [150, 500, 5000, 1000];
CONST speeddata vFast := [500, 1000, 5000, 1000];
CONST speeddata vSlow := [50, 200, 5000, 1000];""",

        'zone_data': """! 区域数据定义
CONST zonedata zFine := [FALSE, 0.3, 0.3, 0.3, 0.03, 0.3, 0.3];
CONST zonedata zMedium := [FALSE, 1.0, 1.0, 1.0, 0.1, 1.0, 1.0];
CONST zonedata zLarge := [FALSE, 5.0, 5.0, 5.0, 0.3, 5.0, 5.0];
CONST zonedata zZero := [FALSE, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0];""",

        'robtarget': """CONST robtarget {point_name} := [
    [{x:.3f}, {y:.3f}, {z:.3f}],
    [{q1:.6f}, {q2:.6f}, {q3:.6f}, {q4:.6f}],
    [0, 0, 0, 0],
    [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];""",

        'proc_header': """PROC {proc_name}()
! {description}
VAR num nCounter;
TPWrite "开始执行: {proc_name}";""",

        'proc_footer': """
TPWrite "完成: {proc_name}";
ENDPROC""",

        'move_instruction': """    MoveL {target_name}, {speed_data}, {zone_data}, {tool_name} \\WObj:={wobj_name};""",

        'movej_instruction': """    MoveJ {target_name}, {speed_data}, {zone_data}, {tool_name} \\WObj:={wobj_name};""",

        'wait_instruction': """    WaitTime {wait_time:.1f};"""
    }

    # 机器人安全位置配置
    SAFE_POSITIONS = {
        'home': {'x': 0, 'y': 0, 'z': 1000, 'q': [1, 0, 0, 0]},
        'safe': {'x': 500, 'y': 0, 'z': 800, 'q': [1, 0, 0, 0]},
        'load': {'x': 300, 'y': 300, 'z': 600, 'q': [0.707, 0, 0.707, 0]}
    }

    def __init__(self, logger=None):
        self.logger = logger
        self.math_model = PolishingMathematicalModel()
        self.advanced_features = AdvancedRAPIDFeatures()

    def generate_complete_program(self, program_data):
        """生成完整的RAPID程序"""
        try:
            if self.logger:
                self.logger.info(f"开始生成工业级RAPID程序: {program_data.get('program_name')}")

            # 1. 生成模块头部
            module_header = self._generate_module_header(program_data)

            # 2. 生成数据声明
            data_declarations = self._generate_data_declarations(program_data)

            # 3. 生成目标点定义
            target_points = self._generate_target_points(program_data)

            # 4. 生成高级功能定义（如果启用）
            advanced_declarations = ""
            if program_data.get('enable_advanced_features', False):
                advanced_declarations = self._generate_advanced_declarations(program_data)

            # 5. 生成子程序
            subprograms = self._generate_subprograms(program_data)

            # 6. 生成高级子程序（如果启用）
            advanced_subprograms = ""
            if program_data.get('enable_advanced_features', False):
                advanced_subprograms = self._generate_advanced_subprograms(program_data)

            # 7. 生成主程序
            main_program = self._generate_main_program(program_data)

            # 8. 生成工具函数
            utility_functions = self._generate_utility_functions(program_data)

            # 9. 组合所有部分
            complete_program = (
                    module_header + "\n" +
                    data_declarations + "\n\n" +
                    advanced_declarations + "\n\n" +
                    target_points + "\n\n" +
                    subprograms + "\n\n" +
                    advanced_subprograms + "\n\n" +
                    main_program + "\n\n" +
                    utility_functions + "\n"
                                        "ENDMODULE"
            )

            # 10. 格式化和验证
            complete_program = self._format_program(complete_program)

            # 11. 添加签名
            complete_program += self._generate_signature()

            if self.logger:
                lines = complete_program.count('\n')
                self.logger.info(f"RAPID程序生成完成: {lines}行")

            return complete_program

        except Exception as e:
            if self.logger:
                self.logger.error(f"生成RAPID程序失败: {e}")
            raise

    def _generate_module_header(self, data):
        """生成模块头部"""
        params = {
            'module_name': data.get('program_name', 'Polishing_Program'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'robot_model': data.get('robot_model', 'IRB 2600-12/1.85'),
            'tool_name': data.get('tool_name', 'tPolishingTool'),
            'tool_diameter': data.get('tool_diameter', 8.0),
            'workpiece_name': data.get('workpiece_name', 'Workpiece'),
            'feature_count': data.get('feature_count', 0),
            'optimization_level': data.get('optimization_level', '高级数学建模')
        }
        return self.RAPID_TEMPLATES['module_header'].format(**params)

    def _generate_data_declarations(self, data):
        """生成数据声明"""
        declarations = []

        # 工具数据
        tool_params = {
            'tool_name': data.get('tool_name', 'tPolishingTool'),
            'tool_length': data.get('tool_length', 200.0),
            'tool_mass': data.get('tool_mass', 0.5),
            'tool_cg_z': data.get('tool_length', 200.0) / 2,
            'inertia_ix': data.get('inertia_ix', 0.001),
            'inertia_iy': data.get('inertia_iy', 0.001),
            'inertia_iz': data.get('inertia_iz', 0.001)
        }
        declarations.append(self.RAPID_TEMPLATES['tool_data'].format(**tool_params))

        # 工件坐标系
        wobj_params = {
            'wobj_name': data.get('wobj_name', 'wWorkpiece'),
            'wobj_uframe': data.get('wobj_uframe', 'Workpiece'),
            'wobj_offset_x': data.get('wobj_offset_x', 0.0),
            'wobj_offset_y': data.get('wobj_offset_y', 0.0),
            'wobj_offset_z': data.get('wobj_offset_z', 0.0),
            'wobj_q1': 1.0, 'wobj_q2': 0.0, 'wobj_q3': 0.0, 'wobj_q4': 0.0
        }
        declarations.append(self.RAPID_TEMPLATES['wobj_data'].format(**wobj_params))

        # 速度数据
        speed_params = {
            'rough_speed': data.get('rough_speed', 300),
            'fine_speed': data.get('fine_speed', 200)
        }
        declarations.append(self.RAPID_TEMPLATES['speed_data'].format(**speed_params))

        # 区域数据
        declarations.append(self.RAPID_TEMPLATES['zone_data'])

        # 安全位置
        declarations.append(self._generate_safe_positions())

        # IO信号定义
        declarations.append(self._generate_io_declarations())

        return "\n\n".join(declarations)

    def _generate_advanced_declarations(self, data):
        """生成高级功能声明"""
        declarations = []

        # 力控制数据
        force_params = data.get('force_params', {
            'max_force': 50.0,
            'compliance': 0.1,
            'target_force': 30.0
        })

        declarations.append("""! ========================================================
! 高级功能定义
! ========================================================""")

        declarations.append("""! 力控制参数
CONST forcedata fRoughPolishing := [
    1,
    [[0, 0, 0.5], [1, 0, 0, 0]],
    50, 9E9
];

CONST forcedata fFinePolishing := [
    1,
    [[0, 0, 0.3], [1, 0, 0, 0]],
    30, 9E9
];""")

        # 优化参数
        optimization_params = data.get('optimization_params', {
            'acceleration': 0.8,
            'jerk': 0.5,
            'corner_radius': 10.0,
            'max_accel': 5000.0,
            'max_decel': 5000.0,
            'path_resolution': 1.0
        })

        declarations.append(f"""! 运动优化参数
CONST optdata optPolishing := [
    [{optimization_params['acceleration']},
     {optimization_params['jerk']},
     {optimization_params['corner_radius']}],
    [TRUE, TRUE, TRUE, TRUE, TRUE]
];""")

        # 数学建模参数
        declarations.append("""! 数学建模参数
PERS num nSurfaceCurvature := 0.01;
PERS num nMaterialRemovalRate := 1.0E-8;
PERS num nContactPressure := 30.0;
PERS num nToolWearFactor := 0.001;""")

        return "\n\n".join(declarations)

    def _generate_safe_positions(self):
        """生成安全位置"""
        safe_positions = []

        for name, pos in self.SAFE_POSITIONS.items():
            target_params = {
                'point_name': f'p{name.capitalize()}',
                'x': pos['x'],
                'y': pos['y'],
                'z': pos['z'],
                'q1': pos['q'][0],
                'q2': pos['q'][1],
                'q3': pos['q'][2],
                'q4': pos['q'][3]
            }
            safe_positions.append(self.RAPID_TEMPLATES['robtarget'].format(**target_params))

        return "! 安全位置定义\n" + "\n".join(safe_positions)

    def _generate_io_declarations(self):
        """生成IO信号声明"""
        return """! IO信号定义
VAR signaldo doSpindleStart;      ! 主轴启动
VAR signaldo doCoolantOn;         ! 冷却液开启
VAR signaldo doToolChange;        ! 工具更换
VAR signaldo doPartClamp;         ! 工件夹紧
VAR signaldo doAirBlow;           ! 吹气清洁

VAR signaldi diSpindleReady;      ! 主轴就绪
VAR signaldi diEmergencyStop;     ! 急停信号
VAR signaldi diDoorClosed;        ! 安全门关闭
VAR signaldi diPartPresent;       ! 工件在位
VAR signaldi diToolInPlace;       ! 工具在位
VAR signaldi diForceSensor;       ! 力传感器就绪

! 力控制参数
PERS forcedata fRoughPolishing := [1, [[0, 0, 0.5], [1, 0, 0, 0]], 50, 9E9];
PERS forcedata fFinePolishing := [1, [[0, 0, 0.3], [1, 0, 0, 0]], 30, 9E9];"""

    def _generate_target_points(self, data):
        """生成目标点定义"""
        targets = []

        # 从路径数据生成目标点
        paths = data.get('paths', {})
        feature_points = data.get('feature_points', [])

        # 特征点定义
        if feature_points:
            targets.append("! 特征点定义")
            for i, point in enumerate(feature_points[:20]):  # 限制数量
                position = point.get('position', [0, 0, 0])
                orientation = point.get('orientation', [1, 0, 0, 0])
                target_params = {
                    'point_name': f'P_Feature_{i:03d}',
                    'x': position[0],
                    'y': position[1],
                    'z': position[2],
                    'q1': orientation[0],
                    'q2': orientation[1],
                    'q3': orientation[2],
                    'q4': orientation[3]
                }
                targets.append(self.RAPID_TEMPLATES['robtarget'].format(**target_params))

        # 路径点定义
        for stage in ['rough', 'fine']:
            if stage in paths and paths[stage]:
                targets.append(f"\n! {stage.capitalize()}抛光目标点")
                for path_idx, path in enumerate(paths[stage][:5]):  # 限制数量
                    points = path.get('points', [])
                    for point_idx, point in enumerate(points[:10]):  # 每个路径最多10个点
                        position = point.get('position', [0, 0, 0])
                        orientation = point.get('orientation', [1, 0, 0, 0])
                        target_params = {
                            'point_name': f'P_{stage[:1].upper()}{path_idx:02d}_{point_idx:03d}',
                            'x': position[0],
                            'y': position[1],
                            'z': position[2],
                            'q1': orientation[0],
                            'q2': orientation[1],
                            'q3': orientation[2],
                            'q4': orientation[3]
                        }
                        targets.append(self.RAPID_TEMPLATES['robtarget'].format(**target_params))

        return "\n".join(targets) if targets else "! 没有生成目标点"

    def _generate_subprograms(self, data):
        """生成子程序"""
        subprograms = []

        # 粗抛子程序
        if data.get('include_rough', True):
            rough_proc = self._generate_polishing_procedure('rough', data)
            subprograms.append(rough_proc)

        # 精抛子程序
        if data.get('include_fine', True):
            fine_proc = self._generate_polishing_procedure('fine', data)
            subprograms.append(fine_proc)

        # 工具更换子程序
        toolchange_proc = self._generate_toolchange_procedure()
        subprograms.append(toolchange_proc)

        # 测量子程序
        measure_proc = self._generate_measurement_procedure()
        subprograms.append(measure_proc)

        # 清洁子程序
        cleaning_proc = self._generate_cleaning_procedure()
        subprograms.append(cleaning_proc)

        return "\n\n".join(subprograms)

    def _generate_advanced_subprograms(self, data):
        """生成高级子程序"""
        subprograms = []

        subprograms.append("""! ========================================================
! 高级功能子程序
! ========================================================""")

        # 数学建模抛光程序
        math_polishing = self._generate_math_model_polishing(data)
        subprograms.append(math_polishing)

        # 力控制抛光程序
        if data.get('enable_force_control', True):
            force_polishing = self._generate_force_control_procedure(data)
            subprograms.append(force_polishing)

        # 优化运动程序
        if data.get('enable_motion_optimization', True):
            optimized_motion = self._generate_optimized_motion_procedure(data)
            subprograms.append(optimized_motion)

        # 自适应抛光程序
        adaptive_polishing = self._generate_adaptive_polishing_procedure(data)
        subprograms.append(adaptive_polishing)

        # 错误恢复程序
        error_recovery = AdvancedRAPIDFeatures.generate_error_recovery_code()
        subprograms.append(error_recovery)

        return "\n\n".join(subprograms)

    def _generate_math_model_polishing(self, data):
        """生成数学建模抛光程序"""
        return """PROC MathModelPolishing()
    ! 数学建模抛光程序
    TPWrite "开始数学建模抛光...";

    ! 数学参数初始化
    VAR num nCurvatureFactor := 0.0;
    VAR num nPressure := 30.0;
    VAR num nSpeed := 200.0;
    VAR num nRemovalRate := 0.0;

    ! 基于曲率调整抛光参数
    FOR i FROM 1 TO 10 DO
        ! 计算曲率因子
        nCurvatureFactor := nSurfaceCurvature * (i / 10.0);

        ! 调整压力和速度
        nPressure := 30.0 + nCurvatureFactor * 20.0;
        nSpeed := 200.0 - nCurvatureFactor * 100.0;

        ! 计算材料去除率
        nRemovalRate := nMaterialRemovalRate * nPressure * nSpeed;

        ! 设置力控制
        ForceDef fMathPolishing, [[0, 0, nPressure]], tPolishingTool;
        ForceAct fMathPolishing;

        ! 执行数学建模抛光
        MoveL pMathPoint, nSpeed, zFine, tPolishingTool \\WObj:=wWorkpiece;

        ! 等待材料去除
        WaitTime nRemovalRate * 0.1;

        TPWrite "曲率因子: " \\Num:=nCurvatureFactor;
        TPWrite "压力: " \\Num:=nPressure;
        TPWrite "去除率: " \\Num:=nRemovalRate;
    ENDFOR

    ! 禁用力控制
    StopForce;

    TPWrite "数学建模抛光完成";
ENDPROC"""

    def _generate_force_control_procedure(self, data):
        """生成力控制抛光程序"""
        force_params = data.get('force_params', {
            'max_force': 50.0,
            'compliance': 0.1,
            'target_force': 30.0
        })

        return f"""PROC ForceControlPolishing()
    ! 力控制抛光程序
    TPWrite "开始力控制抛光...";

    ! 力控制初始化
    ForceDef fForcePolishing, [[0, 0, {force_params['target_force']}]], tPolishingTool;
    ForceAct fForcePolishing;

    ! 力控制抛光循环
    FOR i FROM 1 TO 5 DO
        ! 搜索接触点
        SearchL \\Force, fForcePolishing, pApproach, vSlow, tPolishingTool \\WObj:=wWorkpiece;

        ! 力控制抛光
        ForceL [[0, 0, {force_params['target_force']}]], fForcePolishing, vFine, zZero, tPolishingTool \\WObj:=wWorkpiece;

        ! 力反馈监控
        IF ForceL\\ForceZ > {force_params['max_force']} * 0.9 THEN
            TPWrite "警告: 接近最大力限制";
            nPressure := nPressure * 0.9;
            ForceDef fForcePolishing, [[0, 0, nPressure]], tPolishingTool;
        ENDIF

        ! 移动到下一个点
        MoveL Offs(pForcePath, 0, i*10, 0), vFine, zFine, tPolishingTool \\WObj:=wWorkpiece;
    ENDFOR

    ! 禁用力控制
    StopForce;

    TPWrite "力控制抛光完成";
ENDPROC"""

    def _generate_optimized_motion_procedure(self, data):
        """生成优化运动程序"""
        return """PROC OptimizedMotion()
    ! 优化运动程序
    TPWrite "开始优化运动...";

    ! 应用优化参数
    PathAccLim \\AccLim, 5000, 5000;
    PathResol \\CirPathRes, 1.0;

    ! 平滑运动设置
    SingArea \\Wrist;
    ConfL \\Off;

    ! 执行优化运动
    MoveL pPathStart, vRough \\T:=optPolishing, tPolishingTool \\WObj:=wWorkpiece;
    MoveC pPathArc1, pPathArc2, vRough \\T:=optPolishing, tPolishingTool \\WObj:=wWorkpiece;
    MoveL pPathEnd, vRough \\T:=optPolishing, tPolishingTool \\WObj:=wWorkpiece;

    ! 优化评估
    VAR num nMotionTime := 0.0;
    VAR num nPathAccuracy := 0.0;

    ! 记录运动时间
    nMotionTime := ClkRead();

    TPWrite "优化运动完成";
    TPWrite "运动时间: " \\Num:=nMotionTime;
ENDPROC"""

    def _generate_adaptive_polishing_procedure(self, data):
        """生成自适应抛光程序"""
        return """PROC AdaptivePolishing()
    ! 自适应抛光程序
    TPWrite "开始自适应抛光...";

    ! 自适应参数
    VAR num nSurfaceCurvature := 0.0;
    VAR num nAdaptiveForce := 30.0;
    VAR num nAdaptiveSpeed := 200.0;
    VAR num nCoverage := 0.0;

    ! 表面探测
    TPWrite "探测表面曲率...";
    SearchL \\Force, fFinePolishing, pSurfaceProbe, vSlow, tPolishingTool \\WObj:=wWorkpiece;

    ! 计算自适应参数
    nSurfaceCurvature := ABS(ForceL\\ForceZ) / 50.0;
    nAdaptiveForce := 20.0 + nSurfaceCurvature * 30.0;
    nAdaptiveSpeed := 250.0 - nSurfaceCurvature * 100.0;

    ! 设置自适应抛光
    ForceDef fAdaptive, [[0, 0, nAdaptiveForce]], tPolishingTool;
    ForceAct fAdaptive;

    ! 自适应抛光循环
    FOR i FROM 1 TO 8 DO
        ! 基于曲率调整参数
        IF nSurfaceCurvature > 0.5 THEN
            ! 高曲率区域
            nAdaptiveForce := nAdaptiveForce * 0.8;
            nAdaptiveSpeed := nAdaptiveSpeed * 1.2;
        ELSE
            ! 低曲率区域
            nAdaptiveForce := nAdaptiveForce * 1.2;
            nAdaptiveSpeed := nAdaptiveSpeed * 0.8;
        ENDIF

        ! 执行自适应抛光
        ForceL [[0, 0, nAdaptiveForce]], fAdaptive, nAdaptiveSpeed, zFine, tPolishingTool \\WObj:=wWorkpiece;

        ! 更新覆盖率
        nCoverage := nCoverage + 12.5;
        TPWrite "覆盖率: " \\Num:=nCoverage \\NoNewLine;
        TPWrite "%";
    ENDFOR

    ! 禁用力控制
    StopForce;

    TPWrite "自适应抛光完成";
ENDPROC"""

    def _generate_polishing_procedure(self, stage, data):
        """生成抛光子程序"""
        proc_name = f"Polishing_{stage.capitalize()}"
        description = f"{stage.capitalize()}抛光工艺流程"

        # 程序头部
        proc_content = self.RAPID_TEMPLATES['proc_header'].format(
            proc_name=proc_name,
            description=description
        )

        # 安全检查
        proc_content += """
    ! 安全检查
    IF diEmergencyStop = 0 THEN
        TPWrite "紧急停止激活!";
        EmergencyStop;
        RETURN;
    ENDIF

    IF diDoorClosed = 0 THEN
        TPWrite "安全门未关闭!";
        Stop;
        RETURN;
    ENDIF

    IF diPartPresent = 0 THEN
        TPWrite "工件不在位!";
        Stop;
        RETURN;
    ENDIF"""

        # 启动设备
        proc_content += """
    ! 启动抛光设备
    TPWrite "启动抛光设备...";
    SetDO doSpindleStart, 1;
    SetDO doCoolantOn, 1;

    ! 等待设备就绪
    WaitDI diSpindleReady, 1, \\MaxTime:=10.0;
    IF diSpindleReady = 0 THEN
        TPWrite "抛光设备未就绪!";
        SetDO doSpindleStart, 0;
        SetDO doCoolantOn, 0;
        Stop;
        RETURN;
    ENDIF"""

        # 移动到安全位置
        proc_content += """
    ! 移动到安全位置
    MoveJ pSafe, vFast, zLarge, tPolishingTool \\WObj:=wWorkpiece;"""

        # 添加抛光路径
        paths = data.get('paths', {}).get(stage, [])
        if paths:
            proc_content += f"""
    ! 执行{stage}抛光
    TPWrite "开始{stage}抛光...";"""

            for path_idx, path in enumerate(paths[:3]):  # 最多3个路径
                points = path.get('points', [])
                if points:
                    proc_content += f"""
    ! 路径 {path_idx + 1}
    TPWrite "执行路径 {path_idx + 1}...";"""

                    # 添加入刀点
                    if len(points) > 0:
                        lead_in_point = {
                            'position': [
                                points[0]['position'][0],
                                points[0]['position'][1],
                                points[0]['position'][2] + data.get('safety_height', 50.0)
                            ],
                            'orientation': points[0]['orientation']
                        }

                        # 移动到入刀点
                        target_name = f'P_LeadIn_{stage[:1].upper()}{path_idx:02d}'
                        move_params = {
                            'target_name': target_name,
                            'speed_data': 'vApproach',
                            'zone_data': 'zMedium',
                            'tool_name': data.get('tool_name', 'tPolishingTool'),
                            'wobj_name': data.get('wobj_name', 'wWorkpiece')
                        }
                        proc_content += "\n    " + self.RAPID_TEMPLATES['movej_instruction'].format(**move_params)

                    # 添加路径点
                    for i in range(min(5, len(points))):  # 每个路径最多5个点
                        target_name = f'P_{stage[:1].upper()}{path_idx:02d}_{i:03d}'
                        speed_data = 'vRough' if stage == 'rough' else 'vFine'
                        zone_data = 'zMedium' if stage == 'rough' else 'zFine'
                        move_params = {
                            'target_name': target_name,
                            'speed_data': speed_data,
                            'zone_data': zone_data,
                            'tool_name': data.get('tool_name', 'tPolishingTool'),
                            'wobj_name': data.get('wobj_name', 'wWorkpiece')
                        }
                        proc_content += "\n    " + self.RAPID_TEMPLATES['move_instruction'].format(**move_params)

        # 停止设备
        proc_content += """
    ! 停止抛光设备
    SetDO doSpindleStart, 0;
    SetDO doCoolantOn, 0;

    ! 返回安全位置
    MoveJ pSafe, vFast, zLarge, tPolishingTool \\WObj:=wWorkpiece;"""

        # 程序尾部
        proc_content += "\n\n" + self.RAPID_TEMPLATES['proc_footer'].format(proc_name=proc_name)

        return proc_content

    def _generate_toolchange_procedure(self):
        """生成工具更换子程序"""
        return """PROC ToolChange()
    ! 工具更换程序
    TPWrite "开始工具更换...";

    ! 移动到工具更换位置
    MoveJ pLoad, vFast, zLarge, tPolishingTool \\WObj:=wWorkpiece;

    ! 等待工具在位信号
    IF diToolInPlace = 0 THEN
        TPWrite "等待工具在位...";
        WaitDI diToolInPlace, 1, \\MaxTime:=30.0;
        IF diToolInPlace = 0 THEN
            TPWrite "工具更换超时!";
            RETURN;
        ENDIF
    ENDIF

    ! 工具更换信号
    SetDO doToolChange, 1;
    WaitTime 3.0;
    SetDO doToolChange, 0;

    ! 确认工具更换完成
    WaitTime 1.0;

    TPWrite "工具更换完成";
ENDPROC"""

    def _generate_measurement_procedure(self):
        """生成测量子程序"""
        return """PROC Measurement()
    ! 工件测量程序
    TPWrite "开始工件测量...";

    ! 移动到测量起始位置
    MoveJ pSafe, vFast, zLarge, tPolishingTool;

    ! 测量逻辑
    ! 这里可以添加激光测量或接触式测量代码
    ! 例如使用SearchL进行接触式测量

    TPWrite "测量完成";
ENDPROC"""

    def _generate_cleaning_procedure(self):
        """生成清洁子程序"""
        return """PROC Cleaning()
    ! 清洁程序
    TPWrite "开始清洁...";

    ! 移动到清洁位置
    MoveJ pSafe, vFast, zLarge, tPolishingTool;

    ! 清洁逻辑
    ! 可以添加吹气或清洁刷控制

    TPWrite "清洁完成";
ENDPROC"""

    def _generate_main_program(self, data):
        """生成主程序"""
        main_content = """PROC main()
    ! 主程序 - 抛光工艺流程
    TPWrite "========================================";
    TPWrite "ABB Polishing Studio - 工业级抛光程序";
    TPWrite "数学建模优化版本 v8.1";
    TPWrite "========================================";

    ! 系统初始化
    Initialize();

    ! 安全检查
    IF NOT CheckSafety() THEN
        TPWrite "安全条件不满足!";
        Stop;
    ENDIF

    ! 确认工件在位
    IF diPartPresent = 0 THEN
        TPWrite "工件不在位!";
        Stop;
    ENDIF

    ! 夹紧工件
    SetDO doPartClamp, 1;
    WaitTime 1.0;

    ! 确认工件夹紧
    TPWrite "工件夹紧完成，开始加工...";"""

        # 添加抛光流程
        if data.get('include_rough', True):
            main_content += """
    ! 粗抛工艺
    TPWrite "=== 粗抛工艺开始 ===";
    Polishing_Rough();
    TPWrite "粗抛工艺完成";

    ! 中间清洁（可选）
    IF {include_cleaning} THEN
        Cleaning();
    ENDIF""".format(include_cleaning="TRUE" if data.get('include_cleaning', False) else "FALSE")

        # 添加高级功能（如果启用）
        if data.get('enable_advanced_features', False):
            main_content += """

    ! 高级数学建模抛光
    TPWrite "=== 数学建模抛光开始 ===";
    MathModelPolishing();
    TPWrite "数学建模抛光完成";

    ! 力控制抛光（可选）
    IF {enable_force_control} THEN
        TPWrite "=== 力控制抛光开始 ===";
        ForceControlPolishing();
        TPWrite "力控制抛光完成";
    ENDIF

    ! 优化运动（可选）
    IF {enable_motion_optimization} THEN
        TPWrite "=== 优化运动开始 ===";
        OptimizedMotion();
        TPWrite "优化运动完成";
    ENDIF

    ! 自适应抛光
    TPWrite "=== 自适应抛光开始 ===";
    AdaptivePolishing();
    TPWrite "自适应抛光完成";""".format(
                enable_force_control="TRUE" if data.get('enable_force_control', True) else "FALSE",
                enable_motion_optimization="TRUE" if data.get('enable_motion_optimization', True) else "FALSE"
            )

        if data.get('include_fine', True):
            main_content += """

    ! 精抛工艺
    TPWrite "=== 精抛工艺开始 ===";
    Polishing_Fine();
    TPWrite "精抛工艺完成";"""

        # 程序结束
        main_content += """

    ! 最终测量
    IF {include_measurement} THEN
        Measurement();
    ENDIF

    ! 松开工件
    SetDO doPartClamp, 0;
    WaitTime 1.0;

    ! 返回安全位置
    MoveJ pHome, vFast, zLarge, tPolishingTool;

    TPWrite "========================================";
    TPWrite "抛光程序执行完成!";
    TPWrite "========================================";
ENDPROC""".format(include_measurement="TRUE" if data.get('include_measurement', False) else "FALSE")

        return main_content

    def _generate_utility_functions(self, data):
        """生成工具函数"""
        return """! ========================================================
! 工具函数
! ========================================================

PROC Initialize()
    ! 系统初始化
    TPWrite "初始化系统...";

    ! 复位所有输出
    SetDO doSpindleStart, 0;
    SetDO doCoolantOn, 0;
    SetDO doToolChange, 0;
    SetDO doPartClamp, 0;
    SetDO doAirBlow, 0;

    ! 重置系统状态
    TPWrite "系统初始化完成";
ENDPROC

PROC CheckSafety() : BOOL
    ! 安全检查
    VAR bool bSafe := TRUE;

    ! 检查急停
    IF diEmergencyStop = 0 THEN
        TPWrite "急停按钮被按下!";
        bSafe := FALSE;
    ENDIF

    ! 检查安全门
    IF diDoorClosed = 0 THEN
        TPWrite "安全门未关闭!";
        bSafe := FALSE;
    ENDIF

    ! 检查工具在位
    IF diToolInPlace = 0 THEN
        TPWrite "工具不在位!";
        bSafe := FALSE;
    ENDIF

    RETURN bSafe;
ENDPROC

PROC EmergencyStop()
    ! 紧急停止处理
    TPWrite "紧急停止!";

    ! 立即停止所有输出
    SetDO doSpindleStart, 0;
    SetDO doCoolantOn, 0;
    SetDO doToolChange, 0;
    SetDO doPartClamp, 0;
    SetDO doAirBlow, 0;

    ! 记录错误
    ErrWrite \\W, "紧急停止", "用户触发紧急停止";

    ! 停止运动
    Stop;
ENDPROC

PROC ErrorHandler(num errNo, string errMsg)
    ! 错误处理程序
    TPWrite "错误代码: " + NumToStr(errNo, 0);
    TPWrite "错误信息: " + errMsg;

    ! 停止所有输出
    SetDO doSpindleStart, 0;
    SetDO doCoolantOn, 0;

    ! 返回安全位置
    MoveJ pSafe, vFast, zLarge, tPolishingTool;

    ! 记录错误
    ErrWrite \\W, "程序错误", errMsg;

    ! 停止程序
    Stop;
ENDPROC

PROC WaitForCondition(signaldi diSignal, num nTimeout)
    ! 等待条件满足
    VAR bool bConditionMet := FALSE;
    VAR num nStartTime := ClkRead();

    WHILE (ClkRead() - nStartTime) < nTimeout AND NOT bConditionMet DO
        IF diSignal = 1 THEN
            bConditionMet := TRUE;
        ENDIF
        WaitTime 0.1;
    ENDWHILE

    IF NOT bConditionMet THEN
        TPWrite "等待条件超时!";
    ENDIF
ENDPROC

PROC CalculateMathParameters(num nCurvature, num nHardness)
    ! 计算数学参数
    ! 输入: nCurvature - 表面曲率, nHardness - 材料硬度
    ! 输出: nPressure - 抛光压力, nSpeed - 抛光速度

    VAR num nPressure;
    VAR num nSpeed;

    ! 基于曲率计算压力
    nPressure := 20.0 + nCurvature * 30.0;

    ! 基于硬度调整速度
    nSpeed := 200.0 - nHardness * 0.5;

    ! 限制参数范围
    nPressure := Min(nPressure, 50.0);
    nSpeed := Max(nSpeed, 50.0);

    TPWrite "计算参数 - 压力: " \\Num:=nPressure;
    TPWrite "计算参数 - 速度: " \\Num:=nSpeed;

    RETURN nPressure, nSpeed;
ENDPROC"""

    def _format_program(self, program):
        """格式化程序（添加注释和空行）"""
        lines = program.split('\n')
        formatted_lines = []

        for line in lines:
            # 保持原有缩进
            formatted_lines.append(line)

            # 在某些关键指令后添加空行
            if any(keyword in line for keyword in
                   ['PROC ', 'ENDPROC', 'MoveJ ', 'MoveL ', 'TPWrite', 'IF ', 'WHILE', 'FOR ', 'ENDFOR']):
                if not line.strip().startswith('!'):
                    formatted_lines.append('')

        return '\n'.join(formatted_lines)

    def _generate_signature(self):
        """生成程序签名"""
        return f"""
! ========================================================
! 程序签名
! 生成工具: ABB Polishing Studio {AppConfig.VERSION}
! 数学建模: PolishingMathematicalModel
! 高级功能: AdvancedRAPIDFeatures
! 版权所有: {AppConfig.AUTHOR}
! 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
! ========================================================"""

    def validate_program(self, program):
        """验证RAPID程序语法"""
        errors = []
        warnings = []
        lines = program.split('\n')

        for i, line in enumerate(lines, 1):
            line = line.strip()

            # 检查常见语法错误
            if line.startswith('MoveL') and '\\WObj' not in line:
                warnings.append(f"第{i}行: MoveL指令建议指定工件坐标系")

            if 'IF' in line and 'THEN' not in line and not line.startswith('IF '):
                errors.append(f"第{i}行: IF语句缺少THEN")

            if 'PROC' in line and '()' not in line and not line.startswith('PROC '):
                errors.append(f"第{i}行: 过程定义缺少括号")

            # 检查未闭合的字符串
            if line.count('"') % 2 != 0:
                errors.append(f"第{i}行: 字符串未正确闭合")

        return errors, warnings

    def export_program(self, program, file_path):
        """导出RAPID程序到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(program)
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"导出程序失败: {e}")
            return False


# ==================== 主应用程序类 ====================
class ABBPolishingStudioIndustrialAdvanced:
    """ABB Polishing Studio - 工业级高级主应用程序"""

    def __init__(self):
        # 初始化配置
        AppConfig.ensure_dirs()

        # 创建日志和配置
        self.logger = self._create_logger()
        self.config = self._load_config()

        # 初始化组件
        self.colors = ProfessionalColors()
        self.math_model = PolishingMathematicalModel()
        self.path_planner = None

        # 创建主窗口
        self.root = tk.Tk()
        self._setup_main_window()

        # 初始化处理器
        self.nx_processor = NXSTLProcessor()
        self.rapid_generator = IndustrialRAPIDGenerator(self.logger)

        # 数据存储
        self.current_model = None
        self.model_metadata = {}
        self.features = []
        self.paths = {}
        self.generated_code = ""

        # 数学建模参数
        self.math_params = {
            'surface_curvature': 0.01,
            'material_hardness': 200.0,
            'tool_wear_factor': 0.001,
            'force_distribution': 'uniform',
            'optimization_level': 'high'
        }

        # 创建UI
        self._create_ui()

        # 绑定事件
        self._bind_events()

    def _create_logger(self):
        """创建日志系统"""

        class SimpleLogger:
            def info(self, msg): print(f"[INFO] {msg}")

            def error(self, msg): print(f"[ERROR] {msg}")

            def warning(self, msg): print(f"[WARNING] {msg}")

        return SimpleLogger()

    def _load_config(self):
        """加载配置"""
        return {
            'recent_files': [],
            'robot_model': AppConfig.SUPPORTED_ROBOTS[0],
            'tool_type': AppConfig.SUPPORTED_TOOLS[0],
            'nx_processing': True,
            'enable_math_model': True,
            'enable_advanced_features': True
        }

    def _setup_main_window(self):
        """设置主窗口"""
        self.root.title(f"{AppConfig.APP_NAME} {AppConfig.VERSION}")
        self.root.geometry(f"{AppConfig.DEFAULT_WIDTH}x{AppConfig.DEFAULT_HEIGHT}")
        self.root.minsize(AppConfig.MIN_WIDTH, AppConfig.MIN_HEIGHT)

        # 居中显示
        self.root.eval('tk::PlaceWindow . center')

        # 设置主题
        self.root.configure(bg=self.colors.BACKGROUND)

    def _create_ui(self):
        """创建用户界面"""
        # 创建主容器
        self.main_container = tk.Frame(self.root, bg=self.colors.BACKGROUND)
        self.main_container.pack(fill="both", expand=True, padx=2, pady=2)

        # 创建标题栏
        self._create_title_bar()

        # 创建主内容区域
        self._create_main_content()

        # 创建状态栏
        self._create_status_bar()

    def _create_title_bar(self):
        """创建标题栏"""
        title_frame = tk.Frame(
            self.main_container,
            bg=self.colors.PRIMARY,
            height=60
        )
        title_frame.pack(fill="x", padx=1, pady=(0, 2))
        title_frame.pack_propagate(False)

        # 标题内容
        title_content = tk.Frame(title_frame, bg=self.colors.PRIMARY)
        title_content.pack(fill="both", expand=True, padx=20)

        # 左侧：图标和标题
        left_frame = tk.Frame(title_content, bg=self.colors.PRIMARY)
        left_frame.pack(side="left", fill="y")

        # 图标
        icon_label = tk.Label(
            left_frame,
            text="ZimmerBiomet",
            font=("Segoe UI", 24),
            bg=self.colors.PRIMARY,
            fg="white"
        )
        icon_label.pack(side="left", padx=(0, 15))

        # 标题文字
        title_text = tk.Label(
            left_frame,
            text=f"{AppConfig.APP_NAME} {AppConfig.VERSION}",
            font=("Segoe UI", 16, "bold"),
            bg=self.colors.PRIMARY,
            fg="white"
        )
        title_text.pack(side="left")

        subtitle_text = tk.Label(
            left_frame,
            text="",
            font=("Segoe UI", 10),
            bg=self.colors.PRIMARY,
            fg="#CCCCCC"
        )
        subtitle_text.pack(side="left", padx=(10, 0))

        # 右侧：状态指示器
        right_frame = tk.Frame(title_content, bg=self.colors.PRIMARY)
        right_frame.pack(side="right", fill="y")

        # 连接状态
        self.connection_status = tk.Label(
            right_frame,
            text="● 离线",
            font=("Segoe UI", 10),
            bg=self.colors.PRIMARY,
            fg=self.colors.WARNING_LIGHT
        )
        self.connection_status.pack(side="right", padx=(0, 10))

        # 模型状态
        self.model_status = tk.Label(
            right_frame,
            text="未加载模型",
            font=("Segoe UI", 10),
            bg=self.colors.PRIMARY,
            fg="#AAAAAA"
        )
        self.model_status.pack(side="right", padx=(0, 20))

    def _create_main_content(self):
        """创建主内容区域"""
        # 创建水平分割容器
        h_paned = tk.PanedWindow(
            self.main_container,
            orient="horizontal",
            bg=self.colors.BACKGROUND,
            sashwidth=4,
            sashrelief="raised"
        )
        h_paned.pack(fill="both", expand=True, padx=1, pady=(0, 1))

        # 左侧面板（控制面板）
        self.left_panel = tk.Frame(h_paned, bg=self.colors.BACKGROUND)
        h_paned.add(self.left_panel, width=400)

        # 右侧面板（主视图）
        self.right_panel = tk.Frame(h_paned, bg=self.colors.BACKGROUND)
        h_paned.add(self.right_panel, minsize=800)

        # 创建左侧面板内容
        self._create_left_panel()

        # 创建右侧面板内容
        self._create_right_panel()

    def _create_left_panel(self):
        """创建左侧控制面板"""
        # 创建滚动区域
        left_canvas = tk.Canvas(self.left_panel, bg=self.colors.BACKGROUND, highlightthickness=0)
        left_scrollbar = tk.Scrollbar(self.left_panel, orient="vertical", command=left_canvas.yview)
        left_scrollable = tk.Frame(left_canvas, bg=self.colors.BACKGROUND)

        left_scrollable.bind(
            "<Configure>",
            lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        )

        left_canvas.create_window((0, 0), window=left_scrollable, anchor="nw", width=390)
        left_canvas.configure(yscrollcommand=left_scrollbar.set)

        left_canvas.pack(side="left", fill="both", expand=True)
        left_scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮
        left_canvas.bind_all("<MouseWheel>", lambda e: left_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # 创建内容区域
        content_padding = 12
        content_frame = tk.Frame(left_scrollable, bg=self.colors.BACKGROUND, padx=content_padding, pady=content_padding)
        content_frame.pack(fill="both", expand=True)

        # 1. NX STL处理卡片
        self._create_nx_processing_card(content_frame)

        # 2. 数学建模卡片
        self._create_math_model_card(content_frame)

        # 3. 机器人配置卡片
        self._create_robot_config_card(content_frame)

        # 4. 工具配置卡片
        self._create_tool_config_card(content_frame)

        # 5. 工艺配置卡片
        self._create_process_config_card(content_frame)

        # 6. 路径规划卡片
        self._create_path_planning_card(content_frame)

        # 7. 高级功能卡片
        self._create_advanced_features_card(content_frame)

        # 8. 代码生成卡片
        self._create_code_generation_card(content_frame)

    def _create_nx_processing_card(self, parent):
        """创建NX STL处理卡片"""
        card = tk.LabelFrame(parent, text="NX STL处理", font=("Segoe UI", 11, "bold"),
                             bg=self.colors.SURFACE, fg=self.colors.TEXT_PRIMARY,
                             padx=12, pady=12)
        card.pack(fill="x", pady=(0, 10))

        # NX处理选项
        self.nx_processing_var = tk.BooleanVar(value=self.config.get('nx_processing', True))
        nx_check = tk.Checkbutton(
            card,
            text="启用NX特殊处理",
            variable=self.nx_processing_var,
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        )
        nx_check.pack(anchor="w", pady=(0, 10))

        # 文件选择
        file_frame = tk.Frame(card, bg=self.colors.SURFACE)
        file_frame.pack(fill="x", pady=(0, 10))

        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(
            file_frame,
            textvariable=self.file_path_var,
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY,
            relief="solid",
            borderwidth=1
        )
        file_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_btn = tk.Button(
            file_frame,
            text="浏览",
            command=self.browse_nx_file,
            font=("Segoe UI", 9),
            bg=self.colors.PRIMARY,
            fg="white",
            relief="raised",
            width=8
        )
        browse_btn.pack(side="right")

        # 加载按钮
        load_btn = tk.Button(
            card,
            text="加载NX STL模型",
            command=self.load_nx_model,
            font=("Segoe UI", 10, "bold"),
            bg=self.colors.INFO,
            fg="white",
            padx=15,
            pady=8,
            relief="raised"
        )
        load_btn.pack(fill="x", pady=(0, 10))

        # NX信息显示
        info_frame = tk.Frame(card, bg=self.colors.SURFACE)
        info_frame.pack(fill="x")

        self.nx_info_text = tk.Text(
            info_frame,
            height=6,
            font=("Segoe UI", 9),
            bg=self.colors.SURFACE_LIGHT,
            fg=self.colors.TEXT_SECONDARY,
            relief="flat",
            borderwidth=1,
            wrap="word"
        )
        self.nx_info_text.pack(fill="x")
        self.nx_info_text.insert("1.0", "等待加载NX STL文件...")
        self.nx_info_text.configure(state="disabled")

    def _create_math_model_card(self, parent):
        """创建数学建模卡片"""
        card = tk.LabelFrame(parent, text="数学建模参数", font=("Segoe UI", 11, "bold"),
                             bg=self.colors.SURFACE, fg=self.colors.TEXT_PRIMARY,
                             padx=12, pady=12)
        card.pack(fill="x", pady=(0, 10))

        # 启用数学建模
        self.enable_math_model_var = tk.BooleanVar(value=self.config.get('enable_math_model', True))
        math_check = tk.Checkbutton(
            card,
            text="启用数学建模优化",
            variable=self.enable_math_model_var,
            font=("Segoe UI", 10, "bold"),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        )
        math_check.pack(anchor="w", pady=(0, 10))

        # 表面曲率参数
        curvature_frame = tk.Frame(card, bg=self.colors.SURFACE)
        curvature_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            curvature_frame,
            text="表面曲率系数:",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        ).pack(side="left")

        self.curvature_var = tk.DoubleVar(value=0.01)
        curvature_spin = tk.Spinbox(
            curvature_frame,
            from_=0.001,
            to=0.1,
            increment=0.001,
            textvariable=self.curvature_var,
            width=8,
            font=("Segoe UI", 10)
        )
        curvature_spin.pack(side="right")

        # 材料硬度参数
        hardness_frame = tk.Frame(card, bg=self.colors.SURFACE)
        hardness_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            hardness_frame,
            text="材料硬度 (HV):",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        ).pack(side="left")

        self.hardness_var = tk.DoubleVar(value=200.0)
        hardness_spin = tk.Spinbox(
            hardness_frame,
            from_=50.0,
            to=800.0,
            increment=10.0,
            textvariable=self.hardness_var,
            width=8,
            font=("Segoe UI", 10)
        )
        hardness_spin.pack(side="right")

        # 力分布类型
        force_frame = tk.Frame(card, bg=self.colors.SURFACE)
        force_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            force_frame,
            text="力分布类型:",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        ).pack(side="left")

        self.force_distribution_var = tk.StringVar(value="uniform")
        force_combo = ttk.Combobox(
            force_frame,
            textvariable=self.force_distribution_var,
            values=["uniform", "gradient", "adaptive"],
            state="readonly",
            width=12,
            font=("Segoe UI", 10)
        )
        force_combo.pack(side="right")

        # 优化级别
        optimization_frame = tk.Frame(card, bg=self.colors.SURFACE)
        optimization_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            optimization_frame,
            text="优化级别:",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        ).pack(side="left")

        self.optimization_level_var = tk.StringVar(value="high")
        optimization_combo = ttk.Combobox(
            optimization_frame,
            textvariable=self.optimization_level_var,
            values=["low", "medium", "high"],
            state="readonly",
            width=12,
            font=("Segoe UI", 10)
        )
        optimization_combo.pack(side="right")

    def _create_robot_config_card(self, parent):
        """创建机器人配置卡片"""
        card = tk.LabelFrame(parent, text="机器人配置", font=("Segoe UI", 11, "bold"),
                             bg=self.colors.SURFACE, fg=self.colors.TEXT_PRIMARY,
                             padx=12, pady=12)
        card.pack(fill="x", pady=(0, 10))

        # 机器人型号选择
        model_frame = tk.Frame(card, bg=self.colors.SURFACE)
        model_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            model_frame,
            text="机器人型号:",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        ).pack(side="left")

        self.robot_model_var = tk.StringVar(value=self.config.get('robot_model', AppConfig.SUPPORTED_ROBOTS[0]))
        robot_model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.robot_model_var,
            values=AppConfig.SUPPORTED_ROBOTS,
            state="readonly",
            width=20,
            font=("Segoe UI", 10)
        )
        robot_model_combo.pack(side="right")

        # 机器人信息显示
        info_frame = tk.Frame(card, bg=self.colors.SURFACE)
        info_frame.pack(fill="x")

        self.robot_info_text = tk.Text(
            info_frame,
            height=4,
            font=("Segoe UI", 9),
            bg=self.colors.SURFACE_LIGHT,
            fg=self.colors.TEXT_SECONDARY,
            relief="flat",
            borderwidth=1,
            wrap="word"
        )
        self.robot_info_text.pack(fill="x")
        self.robot_info_text.insert("1.0", self._get_robot_info())
        self.robot_info_text.configure(state="disabled")

    def _get_robot_info(self):
        """获取机器人信息"""
        robot_info = {
            "IRB 2600-12/1.85": "负载: 12kg | 范围: 1850mm | 重复精度: ±0.05mm",
            "IRB 4600-40/2.55": "负载: 40kg | 范围: 2550mm | 重复精度: ±0.05mm",
            "IRB 6700-300/2.70": "负载: 300kg | 范围: 2700mm | 重复精度: ±0.06mm",
            "IRB 14000-0.5/0.9": "负载: 0.5kg | 范围: 900mm | 重复精度: ±0.02mm",
            "IRB 1100-4/0.58": "负载: 4kg | 范围: 580mm | 重复精度: ±0.02mm",
            "IRB 6700F-200/2.70": "负载: 200kg | 范围: 2700mm | 重复精度: ±0.06mm",
            "IRB 8700-550/3.20": "负载: 550kg | 范围: 3200mm | 重复精度: ±0.08mm",
            "自定义机器人": "请自定义机器人参数"
        }
        return robot_info.get(self.robot_model_var.get(), "选择机器人型号查看参数")

    def _create_tool_config_card(self, parent):
        """创建工具配置卡片"""
        card = tk.LabelFrame(parent, text="工具配置", font=("Segoe UI", 11, "bold"),
                             bg=self.colors.SURFACE, fg=self.colors.TEXT_PRIMARY,
                             padx=12, pady=12)
        card.pack(fill="x", pady=(0, 10))

        # 工具类型选择
        tool_frame = tk.Frame(card, bg=self.colors.SURFACE)
        tool_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            tool_frame,
            text="工具类型:",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        ).pack(side="left")

        self.tool_type_var = tk.StringVar(value=self.config.get('tool_type', AppConfig.SUPPORTED_TOOLS[0]))
        tool_type_combo = ttk.Combobox(
            tool_frame,
            textvariable=self.tool_type_var,
            values=AppConfig.SUPPORTED_TOOLS,
            state="readonly",
            width=15,
            font=("Segoe UI", 10)
        )
        tool_type_combo.pack(side="right")

        # 工具参数
        param_frame = tk.Frame(card, bg=self.colors.SURFACE)
        param_frame.pack(fill="x", pady=(0, 8))

        # 工具直径
        tk.Label(
            param_frame,
            text="工具直径:",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.tool_diameter_var = tk.DoubleVar(value=8.0)
        tool_diameter_spin = tk.Spinbox(
            param_frame,
            from_=2.0,
            to=20.0,
            increment=0.5,
            textvariable=self.tool_diameter_var,
            width=8,
            font=("Segoe UI", 10)
        )
        tool_diameter_spin.grid(row=0, column=1, sticky="e", pady=(0, 4))

        tk.Label(
            param_frame,
            text="mm",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_TERTIARY
        ).grid(row=0, column=2, sticky="w", padx=(2, 0), pady=(0, 4))

        # 工具长度
        tk.Label(
            param_frame,
            text="工具长度:",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        ).grid(row=1, column=0, sticky="w")

        self.tool_length_var = tk.DoubleVar(value=200.0)
        tool_length_spin = tk.Spinbox(
            param_frame,
            from_=50.0,
            to=500.0,
            increment=10.0,
            textvariable=self.tool_length_var,
            width=8,
            font=("Segoe UI", 10)
        )
        tool_length_spin.grid(row=1, column=1, sticky="e")

        tk.Label(
            param_frame,
            text="mm",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_TERTIARY
        ).grid(row=1, column=2, sticky="w", padx=(2, 0))

    def _create_process_config_card(self, parent):
        """创建工艺配置卡片"""
        card = tk.LabelFrame(parent, text="工艺配置", font=("Segoe UI", 11, "bold"),
                             bg=self.colors.SURFACE, fg=self.colors.TEXT_PRIMARY,
                             padx=12, pady=12)
        card.pack(fill="x", pady=(0, 10))

        # 粗抛参数
        rough_frame = tk.Frame(card, bg=self.colors.SURFACE)
        rough_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            rough_frame,
            text="粗抛速度:",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        ).pack(side="left")

        self.rough_speed_var = tk.DoubleVar(value=300.0)
        rough_speed_spin = tk.Spinbox(
            rough_frame,
            from_=50.0,
            to=500.0,
            increment=10.0,
            textvariable=self.rough_speed_var,
            width=8,
            font=("Segoe UI", 10)
        )
        rough_speed_spin.pack(side="right")

        tk.Label(
            rough_frame,
            text="mm/s",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_TERTIARY
        ).pack(side="right", padx=(2, 0))

        # 精抛参数
        fine_frame = tk.Frame(card, bg=self.colors.SURFACE)
        fine_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            fine_frame,
            text="精抛速度:",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        ).pack(side="left")

        self.fine_speed_var = tk.DoubleVar(value=200.0)
        fine_speed_spin = tk.Spinbox(
            fine_frame,
            from_=50.0,
            to=500.0,
            increment=10.0,
            textvariable=self.fine_speed_var,
            width=8,
            font=("Segoe UI", 10)
        )
        fine_speed_spin.pack(side="right")

        tk.Label(
            fine_frame,
            text="mm/s",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_TERTIARY
        ).pack(side="right", padx=(2, 0))

        # 安全参数
        safety_frame = tk.Frame(card, bg=self.colors.SURFACE)
        safety_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            safety_frame,
            text="安全高度:",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        ).pack(side="left")

        self.safety_height_var = tk.DoubleVar(value=50.0)
        safety_height_spin = tk.Spinbox(
            safety_frame,
            from_=10.0,
            to=200.0,
            increment=5.0,
            textvariable=self.safety_height_var,
            width=8,
            font=("Segoe UI", 10)
        )
        safety_height_spin.pack(side="right")

        tk.Label(
            safety_frame,
            text="mm",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_TERTIARY
        ).pack(side="right", padx=(2, 0))

    def _create_path_planning_card(self, parent):
        """创建路径规划卡片"""
        card = tk.LabelFrame(parent, text="路径规划", font=("Segoe UI", 11, "bold"),
                             bg=self.colors.SURFACE, fg=self.colors.TEXT_PRIMARY,
                             padx=12, pady=12)
        card.pack(fill="x", pady=(0, 10))

        # 路径类型选择
        type_frame = tk.Frame(card, bg=self.colors.SURFACE)
        type_frame.pack(fill="x", pady=(0, 8))

        self.path_type_var = tk.StringVar(value="adaptive")
        tk.Radiobutton(
            type_frame,
            text="自适应路径",
            variable=self.path_type_var,
            value="adaptive",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 10))

        tk.Radiobutton(
            type_frame,
            text="平行线路径",
            variable=self.path_type_var,
            value="parallel",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        ).pack(side="left")

        # 数学优化路径
        math_path_frame = tk.Frame(card, bg=self.colors.SURFACE)
        math_path_frame.pack(fill="x", pady=(0, 8))

        self.math_path_var = tk.BooleanVar(value=True)
        math_path_check = tk.Checkbutton(
            math_path_frame,
            text="数学优化路径",
            variable=self.math_path_var,
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        )
        math_path_check.pack(side="left")

        # 路径参数
        param_frame = tk.Frame(card, bg=self.colors.SURFACE)
        param_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            param_frame,
            text="步距比例:",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.stepover_var = tk.DoubleVar(value=0.5)
        stepover_spin = tk.Spinbox(
            param_frame,
            from_=0.1,
            to=0.8,
            increment=0.05,
            textvariable=self.stepover_var,
            width=8,
            font=("Segoe UI", 10)
        )
        stepover_spin.grid(row=0, column=1, sticky="e", pady=(0, 4))

        # 生成路径按钮
        generate_btn = tk.Button(
            card,
            text="生成数学优化路径",
            command=self.generate_math_paths,
            font=("Segoe UI", 10, "bold"),
            bg=self.colors.WARNING,
            fg="white",
            padx=15,
            pady=8,
            relief="raised"
        )
        generate_btn.pack(fill="x", pady=(0, 10))

        # 路径信息显示
        info_frame = tk.Frame(card, bg=self.colors.SURFACE)
        info_frame.pack(fill="x")

        self.path_info_text = tk.Text(
            info_frame,
            height=6,
            font=("Segoe UI", 9),
            bg=self.colors.SURFACE_LIGHT,
            fg=self.colors.TEXT_SECONDARY,
            relief="flat",
            borderwidth=1,
            wrap="word"
        )
        self.path_info_text.pack(fill="x")
        self.path_info_text.insert("1.0", "等待生成路径...")
        self.path_info_text.configure(state="disabled")

    def _create_advanced_features_card(self, parent):
        """创建高级功能卡片"""
        card = tk.LabelFrame(parent, text="高级功能", font=("Segoe UI", 11, "bold"),
                             bg=self.colors.SURFACE, fg=self.colors.TEXT_PRIMARY,
                             padx=12, pady=12)
        card.pack(fill="x", pady=(0, 10))

        # 启用高级功能
        self.enable_advanced_var = tk.BooleanVar(value=self.config.get('enable_advanced_features', True))
        advanced_check = tk.Checkbutton(
            card,
            text="启用高级功能",
            variable=self.enable_advanced_var,
            font=("Segoe UI", 10, "bold"),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        )
        advanced_check.pack(anchor="w", pady=(0, 10))

        # 力控制选项
        force_frame = tk.Frame(card, bg=self.colors.SURFACE)
        force_frame.pack(fill="x", pady=(0, 8))

        self.enable_force_control_var = tk.BooleanVar(value=True)
        force_check = tk.Checkbutton(
            force_frame,
            text="力控制抛光",
            variable=self.enable_force_control_var,
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        )
        force_check.pack(side="left", padx=(0, 20))

        # 运动优化选项
        motion_frame = tk.Frame(card, bg=self.colors.SURFACE)
        motion_frame.pack(fill="x", pady=(0, 8))

        self.enable_motion_optimization_var = tk.BooleanVar(value=True)
        motion_check = tk.Checkbutton(
            motion_frame,
            text="运动优化",
            variable=self.enable_motion_optimization_var,
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        )
        motion_check.pack(side="left", padx=(0, 20))

        # 自适应抛光选项
        adaptive_frame = tk.Frame(card, bg=self.colors.SURFACE)
        adaptive_frame.pack(fill="x", pady=(0, 8))

        self.enable_adaptive_polishing_var = tk.BooleanVar(value=True)
        adaptive_check = tk.Checkbutton(
            adaptive_frame,
            text="自适应抛光",
            variable=self.enable_adaptive_polishing_var,
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        )
        adaptive_check.pack(side="left")

        # 力控制参数
        force_params_frame = tk.Frame(card, bg=self.colors.SURFACE)
        force_params_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            force_params_frame,
            text="目标力 (N):",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        ).pack(side="left")

        self.target_force_var = tk.DoubleVar(value=30.0)
        target_force_spin = tk.Spinbox(
            force_params_frame,
            from_=10.0,
            to=50.0,
            increment=5.0,
            textvariable=self.target_force_var,
            width=8,
            font=("Segoe UI", 10)
        )
        target_force_spin.pack(side="right")

    def _create_code_generation_card(self, parent):
        """创建代码生成卡片"""
        card = tk.LabelFrame(parent, text="代码生成", font=("Segoe UI", 11, "bold"),
                             bg=self.colors.SURFACE, fg=self.colors.TEXT_PRIMARY,
                             padx=12, pady=12)
        card.pack(fill="x", pady=(0, 10))

        # 程序名称
        name_frame = tk.Frame(card, bg=self.colors.SURFACE)
        name_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            name_frame,
            text="程序名称:",
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        ).pack(side="left")

        self.program_name_var = tk.StringVar(value="Polishing_Program")
        name_entry = tk.Entry(
            name_frame,
            textvariable=self.program_name_var,
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY,
            relief="solid",
            borderwidth=1,
            width=20
        )
        name_entry.pack(side="right")

        # 代码选项
        options_frame = tk.Frame(card, bg=self.colors.SURFACE)
        options_frame.pack(fill="x", pady=(0, 10))

        self.include_io_var = tk.BooleanVar(value=True)
        io_check = tk.Checkbutton(
            options_frame,
            text="包含IO控制",
            variable=self.include_io_var,
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        )
        io_check.pack(side="left", padx=(0, 20))

        self.include_safety_var = tk.BooleanVar(value=True)
        safety_check = tk.Checkbutton(
            options_frame,
            text="包含安全检查",
            variable=self.include_safety_var,
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY
        )
        safety_check.pack(side="left")

        # 代码生成按钮
        code_buttons_frame = tk.Frame(card, bg=self.colors.SURFACE)
        code_buttons_frame.pack(fill="x", pady=(0, 10))

        generate_code_btn = tk.Button(
            code_buttons_frame,
            text="生成高级RAPID代码",
            command=self.generate_advanced_rapid_code,
            font=("Segoe UI", 10, "bold"),
            bg=self.colors.INFO,
            fg="white",
            padx=15,
            pady=8,
            relief="raised"
        )
        generate_code_btn.pack(side="left", padx=(0, 10))

        export_btn = tk.Button(
            code_buttons_frame,
            text="导出程序",
            command=self.export_program,
            font=("Segoe UI", 10, "bold"),
            bg=self.colors.SUCCESS,
            fg="white",
            padx=15,
            pady=8,
            relief="raised"
        )
        export_btn.pack(side="left")

    def _create_right_panel(self):
        """创建右侧主视图面板"""
        # 创建选项卡视图
        self.tab_view = ttk.Notebook(self.right_panel)
        self.tab_view.pack(fill="both", expand=True, padx=1, pady=1)

        # 创建3D预览选项卡
        self.tab_3d = tk.Frame(self.tab_view, bg=self.colors.CODE_BACKGROUND)
        self._create_3d_viewer()
        self.tab_view.add(self.tab_3d, text="3D预览")

        # 创建数学建模选项卡
        self.tab_math = tk.Frame(self.tab_view, bg=self.colors.BACKGROUND)
        self._create_math_model_view()
        self.tab_view.add(self.tab_math, text="数学建模")

        # 创建代码预览选项卡
        self.tab_code = tk.Frame(self.tab_view, bg=self.colors.BACKGROUND)
        self._create_code_preview()
        self.tab_view.add(self.tab_code, text="代码预览")

        # 创建NX信息选项卡
        self.tab_nx = tk.Frame(self.tab_view, bg=self.colors.BACKGROUND)
        self._create_nx_info()
        self.tab_view.add(self.tab_nx, text="NX信息")

        # 创建路径预览选项卡
        self.tab_path = tk.Frame(self.tab_view, bg=self.colors.BACKGROUND)
        self._create_path_preview()
        self.tab_view.add(self.tab_path, text="路径预览")

    def _create_3d_viewer(self):
        """创建3D查看器"""
        if not MATPLOTLIB_AVAILABLE:
            no_lib_label = tk.Label(
                self.tab_3d,
                text="需要安装matplotlib库",
                font=("Segoe UI", 14),
                bg=self.colors.CODE_BACKGROUND,
                fg=self.colors.CODE_TEXT
            )
            no_lib_label.pack(expand=True)
            return

        try:
            # 创建图形
            self.figure = plt.Figure(figsize=(8, 6), dpi=100, facecolor=self.colors.CODE_BACKGROUND)
            self.ax = self.figure.add_subplot(111, projection='3d')

            # 配置3D轴
            self.ax.set_facecolor(self.colors.CODE_BACKGROUND)

            # 创建画布
            self.canvas = FigureCanvasTkAgg(self.figure, self.tab_3d)
            self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=1, pady=1)

            # 初始设置
            self.ax.set_xlabel('X (mm)')
            self.ax.set_ylabel('Y (mm)')
            self.ax.set_zlabel('Z (mm)')
            self.ax.set_title('等待加载NX模型...', color='white')

            # 设置颜色
            self.ax.xaxis.label.set_color('white')
            self.ax.yaxis.label.set_color('white')
            self.ax.zaxis.label.set_color('white')
            self.ax.tick_params(axis='x', colors='white')
            self.ax.tick_params(axis='y', colors='white')
            self.ax.tick_params(axis='z', colors='white')

            # 设置网格
            self.ax.grid(True, color='gray', alpha=0.3)
            self.canvas.draw()

        except Exception as e:
            print(f"3D可视化初始化失败: {e}")

    def _create_math_model_view(self):
        """创建数学建模视图"""
        # 数学建模信息框架
        math_frame = tk.Frame(self.tab_math, bg=self.colors.BACKGROUND)
        math_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 数学建模信息文本
        self.math_info_text = scrolledtext.ScrolledText(
            math_frame,
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY,
            wrap="word",
            height=20
        )
        self.math_info_text.pack(fill="both", expand=True)

        # 设置初始文本
        self.math_info_text.insert("1.0", """IRB 2600 抛光程序自动生成系统软件

基于以下数学模型进行优化：

1. 表面曲率计算
   - 使用PCA分析计算局部曲率
   - 根据曲率调整抛光参数

2. 接触压力模型
   - Hertz接触理论
   - 弹性变形计算
   - 压力分布优化

3. 材料去除率计算
   - Preston方程: MRR = k * P * v
   - 考虑材料硬度
   - 工具磨损补偿

4. 路径优化算法
   - 旅行商问题简化
   - 自适应步距调整
   - 平滑路径生成

5. 力控制模型
   - 力反馈闭环控制
   - 自适应力调整
   - 碰撞检测算法

6. 能量消耗计算
   - 功率消耗模型
   - 效率优化
   - 成本估算

数学建模参数将在此显示...""")
        self.math_info_text.configure(state="disabled")

    def _create_code_preview(self):
        """创建代码预览"""
        # 工具栏
        toolbar = tk.Frame(self.tab_code, bg=self.colors.SURFACE, height=40)
        toolbar.pack(fill="x", padx=10, pady=(10, 0))
        toolbar.pack_propagate(False)

        # 复制按钮
        copy_btn = tk.Button(
            toolbar,
            text="复制代码",
            command=self.copy_code,
            font=("Segoe UI", 9),
            bg=self.colors.PRIMARY,
            fg="white",
            padx=10,
            pady=5,
            relief="raised"
        )
        copy_btn.pack(side="right", padx=(10, 20), pady=5)

        # 保存按钮
        save_btn = tk.Button(
            toolbar,
            text="保存文件",
            command=self.save_code_file,
            font=("Segoe UI", 9),
            bg=self.colors.SUCCESS,
            fg="white",
            padx=10,
            pady=5,
            relief="raised"
        )
        save_btn.pack(side="right", pady=5)

        # 代码预览区域
        code_frame = tk.Frame(self.tab_code, bg=self.colors.CODE_BACKGROUND)
        code_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 创建代码文本区域
        self.code_text = scrolledtext.ScrolledText(
            code_frame,
            font=("Consolas", 10),
            bg=self.colors.CODE_BACKGROUND,
            fg=self.colors.CODE_TEXT,
            relief="flat",
            borderwidth=0,
            wrap="none",
            tabs=(4, 'left')
        )
        self.code_text.pack(fill="both", expand=True)

        # 设置示例代码
        sample_code = self._get_sample_rapid_code()
        self.code_text.insert("1.0", sample_code)

    def _create_nx_info(self):
        """创建NX信息面板"""
        info_frame = tk.Frame(self.tab_nx, bg=self.colors.BACKGROUND)
        info_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # NX信息文本
        self.nx_detail_text = scrolledtext.ScrolledText(
            info_frame,
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY,
            wrap="word",
            height=20
        )
        self.nx_detail_text.pack(fill="both", expand=True)

        # 设置初始文本
        self.nx_detail_text.insert("1.0", "NX STL文件信息将在此显示\n\n"
                                          "功能包括：\n"
                                          "• NX元数据提取\n"
                                          "• 单位系统识别\n"
                                          "• 零件信息读取\n"
                                          "• 几何特征分析\n"
                                          "• 网格质量评估")
        self.nx_detail_text.configure(state="disabled")

    def _create_path_preview(self):
        """创建路径预览"""
        # 路径信息框架
        path_info_frame = tk.Frame(self.tab_path, bg=self.colors.BACKGROUND)
        path_info_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 路径信息文本
        self.path_detail_text = scrolledtext.ScrolledText(
            path_info_frame,
            font=("Segoe UI", 10),
            bg=self.colors.SURFACE,
            fg=self.colors.TEXT_PRIMARY,
            wrap="word",
            height=20
        )
        self.path_detail_text.pack(fill="both", expand=True)

        # 设置初始文本
        self.path_detail_text.insert("1.0", "抛光路径信息将在此显示\n\n"
                                            "路径规划包括：\n"
                                            "• 自适应路径生成\n"
                                            "• 平行线路径规划\n"
                                            "• 安全高度设置\n"
                                            "• 进退刀路径\n"
                                            "• 路径优化处理\n"
                                            "• 数学建模优化")
        self.path_detail_text.configure(state="disabled")

    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = tk.Frame(
            self.main_container,
            bg=self.colors.SURFACE_DARK,
            height=28
        )
        self.status_bar.pack(fill="x", side="bottom", padx=1, pady=(1, 0))
        self.status_bar.pack_propagate(False)

        # 左侧：状态信息
        self.status_label = tk.Label(
            self.status_bar,
            text="就绪 - Polishing Studio IRB 2600 抛光程序自动生成系统软件",
            font=("Segoe UI", 9),
            bg=self.colors.SURFACE_DARK,
            fg=self.colors.TEXT_SECONDARY,
            padx=20
        )
        self.status_label.pack(side="left")

        # 右侧：系统信息
        system_info_frame = tk.Frame(self.status_bar, bg=self.colors.SURFACE_DARK)
        system_info_frame.pack(side="right", padx=20)

        # 时间显示
        self.time_label = tk.Label(
            system_info_frame,
            text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            font=("Segoe UI", 8),
            bg=self.colors.SURFACE_DARK,
            fg=self.colors.TEXT_LIGHT
        )
        self.time_label.pack(side="left")

        # 更新时间显示
        self._update_time()

    def _update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self._update_time)

    def _bind_events(self):
        """绑定事件"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _get_sample_rapid_code(self):
        """获取示例RAPID代码"""
        return """MODULE Polishing_Program
! ========================================================
! Polishing Studio IRB 2600 抛光程序自动生成系统软件
! 基于NX几何特征的智能抛光程序
! 数学建模优化版本
! ========================================================

! 工具数据定义
CONST tooldata tPolishingTool := [
    TRUE,
    [[0, 0, 100.0], [1, 0, 0, 0]],
    [0.500,
     [0, 0, 45.0],
     [1, 0, 0, 0],
     0.001, 0.001, 0.001]
];

! 主程序
PROC main()
    TPWrite "开始抛光程序";

    ! 执行粗抛
    Polishing_Rough();

    ! 执行精抛
    Polishing_Fine();

    TPWrite "抛光完成";
ENDPROC

! 粗抛子程序
PROC Polishing_Rough()
    TPWrite "开始粗抛";

    ! 抛光路径代码...

    TPWrite "粗抛完成";
ENDPROC

! 精抛子程序
PROC Polishing_Fine()
    TPWrite "开始精抛";

    ! 抛光路径代码...

    TPWrite "精抛完成";
ENDPROC

ENDMODULE"""

    # ==================== 主功能方法 ====================

    def browse_nx_file(self):
        """浏览NX文件"""
        file_path = filedialog.askopenfilename(
            title="选择NX STL文件",
            filetypes=AppConfig.SUPPORTED_FORMATS
        )
        if file_path:
            self.file_path_var.set(file_path)

    def load_nx_model(self):
        """加载NX模型"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("警告", "请先选择STL文件")
            return

        if not os.path.exists(file_path):
            messagebox.showerror("错误", "文件不存在")
            return

        # 检查文件扩展名
        if not file_path.lower().endswith('.stl'):
            response = messagebox.askyesno("警告",
                                           f"文件 {os.path.basename(file_path)} 不是.stl文件。\n"
                                           "是否继续尝试加载？")
            if not response:
                return

        # 检查依赖库
        if not TRIMESH_AVAILABLE:
            messagebox.showerror("错误",
                                 "需要安装trimesh库\n"
                                 "请运行: pip install trimesh scikit-learn scipy matplotlib")
            return

        # 更新状态
        self.status_label.config(text="正在加载STL模型...")
        self.root.update()

        try:
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                messagebox.showerror("错误", "文件为空")
                return

            # 检查是否为NX STL（但无论如何都尝试加载）
            is_nx = self.nx_processor.is_nx_stl(file_path)
            force_nx_processing = self.nx_processing_var.get()

            # 使用改进的加载方法
            self.current_model = self.nx_processor.load_stl_with_metadata(
                file_path,
                force_nx_processing=force_nx_processing
            )

            if self.current_model is None:
                raise Exception("STL文件加载失败")

            # 获取元数据
            self.model_metadata = self.current_model.metadata

            # 分析网格特征
            mesh_features = self.nx_processor.analyze_mesh_features(self.current_model)

            # 显示模型信息
            info_text = f"✅ STL文件加载成功!\n\n"
            info_text += f"文件: {os.path.basename(file_path)}\n"
            info_text += f"文件大小: {file_size / 1024:.1f} KB\n"
            info_text += f"格式: {self.model_metadata.get('original_format', 'STL')}\n"

            if self.model_metadata.get('is_nx'):
                info_text += f"类型: NX STL (已应用特殊处理)\n"
            else:
                info_text += f"类型: 标准STL\n"

            info_text += f"单位: {self.model_metadata.get('units', '毫米')}\n"

            if self.model_metadata.get('part_name'):
                info_text += f"零件名称: {self.model_metadata['part_name']}\n"
            if self.model_metadata.get('creation_date'):
                info_text += f"创建日期: {self.model_metadata['creation_date']}\n"
            if self.model_metadata.get('author'):
                info_text += f"作者: {self.model_metadata['author']}\n"
            if self.model_metadata.get('cad_system'):
                info_text += f"CAD系统: {self.model_metadata['cad_system']}\n"

            info_text += f"\n网格信息:\n"
            info_text += f"顶点数: {mesh_features.get('vertex_count', 0):,}\n"
            info_text += f"面片数: {mesh_features.get('triangle_count', 0):,}\n"

            if mesh_features.get('is_watertight') is not None:
                info_text += f"水密性: {'是' if mesh_features['is_watertight'] else '否'}\n"
            if mesh_features.get('is_closed') is not None:
                info_text += f"封闭性: {'是' if mesh_features['is_closed'] else '否'}\n"

            if mesh_features.get('bounding_box'):
                bbox = mesh_features['bounding_box']
                info_text += f"尺寸: {bbox['size'][0]:.1f} × {bbox['size'][1]:.1f} × {bbox['size'][2]:.1f} mm\n"

            if mesh_features.get('surface_area'):
                info_text += f"表面积: {mesh_features['surface_area']:,.1f} mm²\n"
            if mesh_features.get('volume'):
                info_text += f"体积: {mesh_features['volume']:,.1f} mm³\n"

            self.nx_info_text.configure(state="normal")
            self.nx_info_text.delete("1.0", tk.END)
            self.nx_info_text.insert("1.0", info_text)
            self.nx_info_text.configure(state="disabled")

            # 更新详细NX信息
            detail_text = f"STL文件详细分析:\n\n"
            detail_text += f"文件路径: {file_path}\n"
            detail_text += f"文件大小: {file_size / 1024:.1f} KB\n"
            detail_text += f"检测结果: {'NX STL' if self.model_metadata.get('is_nx') else '标准STL'}\n"
            detail_text += f"强制NX处理: {'是' if force_nx_processing else '否'}\n\n"

            detail_text += "元数据:\n"
            for key, value in self.model_metadata.items():
                if value and key not in ['nx_specific']:
                    if isinstance(value, dict):
                        detail_text += f"  {key}:\n"
                        for k2, v2 in value.items():
                            detail_text += f"    {k2}: {v2}\n"
                    else:
                        detail_text += f"  {key}: {value}\n"

            if self.model_metadata.get('nx_specific'):
                detail_text += "\nNX特定信息:\n"
                for key, value in self.model_metadata['nx_specific'].items():
                    detail_text += f"  {key}: {value}\n"

            detail_text += "\n网格特征:\n"
            for key, value in mesh_features.items():
                if value is not None and key != 'bounding_box':
                    if isinstance(value, (list, np.ndarray)):
                        detail_text += f"  {key}: {np.array(value).tolist()}\n"
                    else:
                        detail_text += f"  {key}: {value}\n"

            self.nx_detail_text.configure(state="normal")
            self.nx_detail_text.delete("1.0", tk.END)
            self.nx_detail_text.insert("1.0", detail_text)
            self.nx_detail_text.configure(state="disabled")

            # 更新数学建模信息
            if self.enable_math_model_var.get():
                math_text = f"数学建模分析:\n\n"
                math_text += f"模型顶点数: {mesh_features.get('vertex_count', 0):,}\n"
                math_text += f"模型面片数: {mesh_features.get('triangle_count', 0):,}\n\n"

                # 计算表面曲率（如果模型不太大）
                if mesh_features.get('vertex_count', 0) < 10000:
                    try:
                        curvatures = self.math_model.calculate_surface_curvature(self.current_model)
                        avg_curvature = np.mean(curvatures) if len(curvatures) > 0 else 0
                        math_text += f"平均表面曲率: {avg_curvature:.6f}\n"
                        math_text += f"最大曲率: {np.max(curvatures):.6f}\n"
                        math_text += f"最小曲率: {np.min(curvatures):.6f}\n\n"
                    except Exception as e:
                        math_text += f"曲率计算跳过（顶点过多）\n\n"

                # 计算表面法向量
                try:
                    normals = self.math_model.calculate_surface_normals(self.current_model)
                    math_text += f"表面法向量计算完成\n"
                    math_text += f"法向量数量: {len(normals):,}\n\n"
                except Exception as e:
                    math_text += f"法向量计算失败: {str(e)}\n\n"

                # 计算接触压力
                tool_radius = self.tool_diameter_var.get() / 2
                force = 30.0  # 默认力

                if mesh_features.get('bounding_box'):
                    bbox_size = mesh_features['bounding_box']['size']
                    avg_size = np.mean(bbox_size)
                    estimated_curvature = 1.0 / (avg_size * 0.1)  # 估计曲率
                    contact_pressure = self.math_model.calculate_contact_pressure(tool_radius, force,
                                                                                  estimated_curvature)
                    math_text += f"工具半径: {tool_radius:.1f} mm\n"
                    math_text += f"接触压力: {contact_pressure:.2f} MPa\n\n"

                    # 计算材料去除率
                    removal_rate = self.math_model.calculate_material_removal_rate(contact_pressure, 200.0, tool_radius)
                    math_text += f"材料去除率: {removal_rate:.6f} mm³/s\n"

                self.math_info_text.configure(state="normal")
                self.math_info_text.delete("1.0", tk.END)
                self.math_info_text.insert("1.0", math_text)
                self.math_info_text.configure(state="disabled")

            # 在3D视图中显示模型
            if hasattr(self, 'ax') and self.ax:
                try:
                    self.ax.clear()

                    # 绘制模型
                    vertices = self.current_model.vertices
                    faces = self.current_model.faces

                    # 如果顶点太多，进行采样
                    max_vertices = 5000
                    if len(vertices) > max_vertices:
                        # 随机采样
                        indices = np.random.choice(len(vertices), max_vertices, replace=False)
                        vertices = vertices[indices]
                        # 简化显示，只显示点云
                        self.ax.scatter(
                            vertices[:, 0], vertices[:, 1], vertices[:, 2],
                            c='cyan', alpha=0.6, s=1
                        )
                        self.ax.set_title(f'STL模型: {os.path.basename(file_path)} (点云显示)', color='white')
                    else:
                        # 完整显示
                        self.ax.plot_trisurf(
                            vertices[:, 0], vertices[:, 1], vertices[:, 2],
                            triangles=faces,
                            color='cyan',
                            alpha=0.8,
                            edgecolor='gray',
                            linewidth=0.5
                        )
                        self.ax.set_title(f'STL模型: {os.path.basename(file_path)}', color='white')

                    # 设置视图
                    self.ax.set_xlabel('X (mm)')
                    self.ax.set_ylabel('Y (mm)')
                    self.ax.set_zlabel('Z (mm)')

                    if mesh_features.get('bounding_box'):
                        bbox = mesh_features['bounding_box']
                        # 设置坐标轴范围
                        margin = max(bbox['size']) * 0.1
                        self.ax.set_xlim([bbox['min'][0] - margin, bbox['max'][0] + margin])
                        self.ax.set_ylim([bbox['min'][1] - margin, bbox['max'][1] + margin])
                        self.ax.set_zlim([bbox['min'][2] - margin, bbox['max'][2] + margin])

                    if hasattr(self, 'canvas'):
                        self.canvas.draw()
                except Exception as e:
                    print(f"3D显示错误: {e}")
                    # 显示错误信息
                    self.ax.clear()
                    self.ax.text(0.5, 0.5, 0.5, "3D显示错误", color='red',
                                 horizontalalignment='center', verticalalignment='center')
                    if hasattr(self, 'canvas'):
                        self.canvas.draw()

            # 初始化路径规划器
            try:
                self.path_planner = AdvancedPathPlanner(self.current_model, self.tool_diameter_var.get())
            except Exception as e:
                print(f"初始化路径规划器失败: {e}")
                self.path_planner = None

            # 更新模型状态
            self.model_status.config(text=f"已加载: {os.path.basename(file_path)}")

            if self.model_metadata.get('is_nx'):
                self.status_label.config(text=f"NX STL模型加载成功")
                messagebox.showinfo("成功",
                                    f"STL文件已加载\n"
                                    f"类型: NX STL\n"
                                    f"顶点数: {mesh_features.get('vertex_count', 0):,}\n"
                                    f"面片数: {mesh_features.get('triangle_count', 0):,}")
            else:
                self.status_label.config(text=f"标准STL模型加载成功")
                messagebox.showinfo("成功",
                                    f"STL文件已加载\n"
                                    f"类型: 标准STL\n"
                                    f"顶点数: {mesh_features.get('vertex_count', 0):,}\n"
                                    f"面片数: {mesh_features.get('triangle_count', 0):,}")

        except Exception as e:
            error_msg = f"加载模型失败:\n{str(e)}\n\n"
            error_msg += f"文件: {os.path.basename(file_path)}\n"
            error_msg += f"大小: {file_size / 1024:.1f} KB\n"
            error_msg += "可能的原因:\n"
            error_msg += "1. 文件损坏或不完整\n"
            error_msg += "2. 不是有效的STL格式\n"
            error_msg += "3. 文件编码问题\n"
            error_msg += "4. 内存不足\n"

            messagebox.showerror("错误", error_msg)
            self.status_label.config(text="模型加载失败")
            print(f"详细错误信息: {traceback.format_exc()}")

    def generate_math_paths(self):
        """生成数学优化路径"""
        if self.current_model is None:
            messagebox.showwarning("警告", "请先加载NX模型")
            return

        if self.path_planner is None:
            self.path_planner = AdvancedPathPlanner(self.current_model, self.tool_diameter_var.get())

        # 更新状态
        self.status_label.config(text="正在生成数学优化路径...")

        try:
            # 根据选择的路径类型生成路径
            path_type = self.path_type_var.get()
            math_optimization = self.math_path_var.get()

            if path_type == "adaptive":
                # 生成自适应路径
                paths = self.path_planner.generate_adaptive_path(self.stepover_var.get())
                rough_paths = paths
                fine_paths = []

            elif path_type == "parallel":
                # 生成平行线路径
                rough_paths = self.path_planner.generate_parallel_path(angle=0,
                                                                       spacing=self.tool_diameter_var.get() * 0.7)
                fine_paths = self.path_planner.generate_parallel_path(angle=90,
                                                                      spacing=self.tool_diameter_var.get() * 0.5)

            else:
                # 生成螺旋路径
                spiral_paths = self.path_planner.generate_spiral_path()
                rough_paths = spiral_paths
                fine_paths = []

            # 如果启用数学优化，优化路径序列
            if math_optimization:
                if rough_paths:
                    rough_paths = self.path_planner.optimize_path_sequence(rough_paths)
                if fine_paths:
                    fine_paths = self.path_planner.optimize_path_sequence(fine_paths)

            # 转换为程序所需格式
            self.paths = {
                'rough': self._convert_paths_to_program_format(rough_paths, 'rough'),
                'fine': self._convert_paths_to_program_format(fine_paths, 'fine')
            }

            # 计算路径覆盖率
            coverage = self.path_planner.calculate_path_coverage(rough_paths + fine_paths)

            # 更新路径信息
            info_text = f"✅ 数学优化路径生成成功!\n\n"
            info_text += f"路径类型: {path_type}\n"
            info_text += f"数学优化: {'启用' if math_optimization else '禁用'}\n"
            info_text += f"粗抛路径: {len(self.paths.get('rough', []))} 条\n"
            info_text += f"精抛路径: {len(self.paths.get('fine', []))} 条\n"
            info_text += f"总路径点数: {self._count_total_points(self.paths)}\n"
            info_text += f"步距比例: {self.stepover_var.get() * 100:.0f}%\n"
            info_text += f"路径覆盖率: {coverage * 100:.1f}%\n"
            info_text += f"安全高度: {self.safety_height_var.get():.0f} mm"

            self.path_info_text.configure(state="normal")
            self.path_info_text.delete("1.0", tk.END)
            self.path_info_text.insert("1.0", info_text)
            self.path_info_text.configure(state="disabled")

            # 更新详细路径信息
            detail_text = f"数学优化路径详细分析:\n\n"
            detail_text += f"路径类型: {path_type}\n"
            detail_text += f"工具直径: {self.tool_diameter_var.get()} mm\n"
            detail_text += f"步距: {self.tool_diameter_var.get() * self.stepover_var.get():.2f} mm\n"
            detail_text += f"路径覆盖率: {coverage * 100:.1f}%\n\n"

            total_length = 0
            for stage in ['rough', 'fine']:
                if stage in self.paths and self.paths[stage]:
                    detail_text += f"{stage.capitalize()}抛光:\n"
                    for i, path in enumerate(self.paths[stage][:3]):
                        points = path.get('points', [])
                        detail_text += f"  路径{i + 1}: {len(points)}点\n"
                        if points:
                            # 计算路径长度
                            path_length = 0
                            for j in range(1, len(points)):
                                p1 = points[j - 1]['position']
                                p2 = points[j]['position']
                                path_length += np.linalg.norm(np.array(p2) - np.array(p1))
                            detail_text += f"    长度: {path_length:.1f}mm\n"
                            total_length += path_length

            detail_text += f"\n总路径长度: {total_length:.1f} mm\n"

            # 计算预估加工时间
            rough_time = total_length * 0.7 / self.rough_speed_var.get()
            fine_time = total_length * 0.3 / self.fine_speed_var.get()
            total_time = rough_time + fine_time

            detail_text += f"预估粗抛时间: {rough_time:.1f}秒\n"
            detail_text += f"预估精抛时间: {fine_time:.1f}秒\n"
            detail_text += f"预估总加工时间: {total_time:.1f}秒"

            self.path_detail_text.configure(state="normal")
            self.path_detail_text.delete("1.0", tk.END)
            self.path_detail_text.insert("1.0", detail_text)
            self.path_detail_text.configure(state="disabled")

            # 在3D视图中显示路径
            if hasattr(self, 'ax') and self.ax:
                colors = {
                    'rough': 'red',
                    'fine': 'blue'
                }

                for stage in ['rough', 'fine']:
                    if stage in self.paths and self.paths[stage]:
                        color = colors[stage]
                        for path in self.paths[stage][:2]:  # 只显示前2个路径
                            points = path.get('points', [])
                            if len(points) > 1:
                                points_array = np.array([p['position'] for p in points])
                                self.ax.plot(
                                    points_array[:, 0],
                                    points_array[:, 1],
                                    points_array[:, 2],
                                    color=color,
                                    linewidth=2,
                                    alpha=0.6
                                )

                if hasattr(self, 'canvas'):
                    self.canvas.draw()

            self.status_label.config(text="数学优化路径生成完成")

        except Exception as e:
            messagebox.showerror("错误", f"生成路径失败:\n{str(e)}")
            self.status_label.config(text="路径生成失败")

    def _convert_paths_to_program_format(self, paths, stage):
        """将路径转换为程序格式"""
        program_paths = []

        for i, path in enumerate(paths):
            points = path.get('points', [])

            # 为每个点添加姿态信息
            path_points = []
            for j, point in enumerate(points):
                if isinstance(point, list) and len(point) >= 3:
                    # 计算工具姿态
                    normal = [0, 0, 1]  # 简化，实际应根据表面法向量计算
                    orientation = self.math_model.calculate_tool_orientation(normal)

                    path_points.append({
                        'position': [float(point[0]), float(point[1]), float(point[2])],
                        'orientation': orientation,
                        'velocity': self.rough_speed_var.get() if stage == 'rough' else self.fine_speed_var.get(),
                        'zone': 'zMedium' if stage == 'rough' else 'zFine'
                    })

            if path_points:
                program_paths.append({
                    'id': i,
                    'name': f'{stage.capitalize()}路径_{i + 1}',
                    'points': path_points,
                    'total_length': path.get('total_length', 0.0),
                    'estimated_time': path.get('estimated_time', 0.0)
                })

        return program_paths

    def _count_total_points(self, paths):
        """计算总路径点数"""
        total = 0
        for stage in ['rough', 'fine']:
            if stage in paths:
                for path in paths[stage]:
                    total += len(path.get('points', []))
        return total

    def generate_advanced_rapid_code(self):
        """生成高级RAPID代码"""
        if not self.paths:
            messagebox.showwarning("警告", "请先生成抛光路径")
            return

        # 更新状态
        self.status_label.config(text="正在生成高级RAPID代码...")

        try:
            # 准备数据
            program_data = {
                'program_name': self.program_name_var.get(),
                'robot_model': self.robot_model_var.get(),
                'tool_name': 'tPolishingTool',
                'tool_diameter': self.tool_diameter_var.get(),
                'tool_length': self.tool_length_var.get(),
                'tool_mass': 0.5,
                'workpiece_name': 'Workpiece',
                'rough_speed': self.rough_speed_var.get(),
                'fine_speed': self.fine_speed_var.get(),
                'safety_height': self.safety_height_var.get(),
                'paths': self.paths,
                'include_io': self.include_io_var.get(),
                'include_safety': self.include_safety_var.get(),
                'include_rough': True,
                'include_fine': True,
                'include_measurement': True,
                'include_cleaning': True,
                'feature_count': len(self.features) if self.features else 0,
                'optimization_level': self.optimization_level_var.get(),

                # 高级功能配置
                'enable_advanced_features': self.enable_advanced_var.get(),
                'enable_force_control': self.enable_force_control_var.get(),
                'enable_motion_optimization': self.enable_motion_optimization_var.get(),
                'enable_math_model': self.enable_math_model_var.get(),

                # 力控制参数
                'force_params': {
                    'max_force': 50.0,
                    'compliance': 0.1,
                    'target_force': self.target_force_var.get()
                },

                # 优化参数
                'optimization_params': {
                    'acceleration': 0.8,
                    'jerk': 0.5,
                    'corner_radius': 10.0,
                    'max_accel': 5000.0,
                    'max_decel': 5000.0,
                    'path_resolution': 1.0
                }
            }

            # 生成代码
            self.generated_code = self.rapid_generator.generate_complete_program(program_data)

            # 显示代码
            self.code_text.delete("1.0", tk.END)
            self.code_text.insert("1.0", self.generated_code)

            # 语法验证
            errors, warnings = self.rapid_generator.validate_program(self.generated_code)

            if warnings:
                self.status_label.config(text=f"RAPID代码生成完成，有{len(warnings)}个警告")
            else:
                self.status_label.config(text="高级RAPID代码生成完成")

            # 显示统计信息
            lines = self.generated_code.count('\n')
            features_enabled = []
            if self.enable_math_model_var.get():
                features_enabled.append("数学建模")
            if self.enable_force_control_var.get():
                features_enabled.append("力控制")
            if self.enable_motion_optimization_var.get():
                features_enabled.append("运动优化")

            features_text = "、".join(features_enabled) if features_enabled else "基础"

            messagebox.showinfo("完成",
                                f"工业级高级RAPID代码生成完成\n"
                                f"共 {lines} 行代码\n"
                                f"启用功能: {features_text}\n"
                                f"优化级别: {self.optimization_level_var.get()}")

        except Exception as e:
            messagebox.showerror("错误", f"生成代码失败:\n{str(e)}")
            self.status_label.config(text="代码生成失败")

    def export_program(self):
        """导出程序文件"""
        if not self.generated_code:
            messagebox.showwarning("警告", "请先生成RAPID代码")
            return

        # 选择保存位置
        default_name = f"{self.program_name_var.get()}.mod"
        file_path = filedialog.asksaveasfilename(
            title="保存RAPID程序",
            defaultextension=".mod",
            initialfile=default_name,
            filetypes=[
                ("ABB RAPID程序", "*.mod"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )

        if not file_path:
            return

        # 更新状态
        self.status_label.config(text="正在导出程序...")

        try:
            # 导出程序
            success = self.rapid_generator.export_program(self.generated_code, file_path)

            if success:
                self.status_label.config(text="程序导出成功")
                messagebox.showinfo("成功", f"高级RAPID程序已导出到:\n{file_path}")
            else:
                messagebox.showerror("错误", "导出失败")
                self.status_label.config(text="导出失败")

        except Exception as e:
            messagebox.showerror("错误", f"导出失败:\n{str(e)}")
            self.status_label.config(text="导出失败")

    def copy_code(self):
        """复制代码到剪贴板"""
        if not self.generated_code:
            messagebox.showwarning("警告", "没有可复制的代码")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(self.generated_code)
        self.status_label.config(text="代码已复制到剪贴板")

    def save_code_file(self):
        """保存代码文件"""
        self.export_program()

    def on_closing(self):
        """关闭应用程序"""
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.root.destroy()

    def run(self):
        """运行应用程序"""
        try:
            print("=" * 80)
            print(f"{AppConfig.APP_NAME} - {AppConfig.VERSION}")
            print("工业级机器人抛光解决方案 - 数学建模优化版")
            print("=" * 80)
            self.root.mainloop()
        except Exception as e:
            print(f"应用程序运行错误: {e}")


# ==================== 主程序入口 ====================
def main():
    """主程序入口"""
    print("启动ABB Polishing Studio工业级高级专业版...")

    try:
        # 检查依赖
        if not TRIMESH_AVAILABLE:
            print("警告: 缺少必要的Python库")
            print("部分功能将受限使用")
            print("建议安装: pip install trimesh scikit-learn scipy matplotlib")

        # 创建并运行应用程序
        app = ABBPolishingStudioIndustrialAdvanced()
        app.run()

    except Exception as e:
        print(f"应用程序启动失败: {e}")
        print(traceback.format_exc())

        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "启动失败",
                f"应用程序启动失败:\n\n{str(e)}"
            )
            root.destroy()
        except:
            pass

        sys.exit(1)


if __name__ == "__main__":
    main()
