import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import Dict, Any, Optional


# 假设这些配置已移动到 utils 或 config 模块
# from utils.config import AppConfig, ProfessionalColors

# ==================== 专业 UI 组件库 ====================

class ProfessionalFrame(tk.Frame):
    """专业框架组件 - 提供统一的边距管理"""

    def __init__(self, parent, padding=16, bg=None, **kwargs):
        # 引用配色方案（重构时建议从 utils 导入）
        self.colors = kwargs.pop('colors', None)
        bg = bg or "#F0F0F0"
        super().__init__(parent, bg=bg, **kwargs)
        self.padding = padding


class ProfessionalCard(tk.Frame):
    """专业卡片组件 - 工业级容器"""

    def __init__(self, parent, title="", subtitle="", padding=16, bg="#FFFFFF", **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg="#F0F0F0", highlightbackground="#E0E0E0", highlightthickness=1)

        # 内容容器
        self.content_frame = tk.Frame(self, bg=bg)
        self.content_frame.pack(fill="both", expand=True, padx=1, pady=1)

        if title:
            self.title_frame = tk.Frame(self.content_frame, bg="#F5F5F5", height=40)
            self.title_frame.pack(fill="x", pady=(0, padding))
            self.title_frame.pack_propagate(False)

            tk.Label(self.title_frame, text=title, font=("微软雅黑", 11, "bold"),
                     bg="#F5F5F5", fg="#333333").pack(side="left", padx=padding)
            if subtitle:
                tk.Label(self.title_frame, text=subtitle, font=("微软雅黑", 9),
                         bg="#F5F5F5", fg="#999999").pack(side="right", padx=padding)

        self.body_frame = tk.Frame(self.content_frame, bg=bg)
        self.body_frame.pack(fill="both", expand=True, padx=padding, pady=(0, padding))


class ProfessionalButton(tk.Frame):
    """专业按钮组件 - 增强交互反馈"""

    def __init__(self, parent, text="", command=None, variant="primary", **kwargs):
        super().__init__(parent, **kwargs)
        # 简化版颜色映射
        colors = {
            "primary": {"bg": "#005596", "fg": "white", "hover": "#003D6B"},
            "ghost": {"bg": "#FFFFFF", "fg": "#333333", "hover": "#F5F5F5"},
            "secondary": {"bg": "#07C160", "fg": "white", "hover": "#05A84E"}
        }
        self.style = colors.get(variant, colors["primary"])

        self.btn_frame = tk.Frame(self, bg=self.style["bg"], cursor="hand2")
        self.btn_frame.pack(fill="both", expand=True)

        self.label = tk.Label(self.btn_frame, text=text, fg=self.style["fg"],
                              bg=self.style["bg"], font=("微软雅黑", 10, "bold"), pady=8)
        self.label.pack()

        # 绑定事件
        for item in [self.btn_frame, self.label]:
            item.bind("<Enter>", lambda e: self.btn_frame.config(bg=self.style["hover"]))
            item.bind("<Enter>", lambda e: self.label.config(bg=self.style["hover"]), add="+")
            item.bind("<Leave>", lambda e: self.btn_frame.config(bg=self.style["bg"]))
            item.bind("<Leave>", lambda e: self.label.config(bg=self.style["bg"]), add="+")
            item.bind("<Button-1>", lambda e: command() if command else None)


# ==================== 主 GUI 模块 ====================

class PolishingStudioGUI:
    """ABB Polishing Studio - GUI 逻辑拆分版"""

    def __init__(self, root, core_engine=None):
        self.root = root
        self.core = core_engine  # 传入 Core 模块的引用

        # 状态变量 (原代码中的数据存储)
        self.file_path_var = tk.StringVar()
        self.robot_model_var = tk.StringVar(value="IRB 2600-12/1.85")

        self._setup_window()
        self._create_layout()

    def _setup_window(self):
        self.root.title("ABB Polishing Studio 2.0 - 模块化预览")
        self.root.geometry("1400x850")
        self.root.configure(bg="#F0F0F0")

    def _create_layout(self):
        """三层布局：标题栏、主内容区、状态栏"""
        # 1. 标题栏
        self.header = tk.Frame(self.root, bg="#005596", height=70)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        tk.Label(self.header, text="🏭 ABB Polishing Studio", font=("微软雅黑", 16, "bold"),
                 bg="#005596", fg="white").pack(side="left", padx=25)

        # 2. 主内容区
        self.main_container = tk.Frame(self.root, bg="#F0F0F0", padx=15, pady=15)
        self.main_container.pack(fill="both", expand=True)

        # 左侧面板 (380px)
        self.left_panel = tk.Frame(self.main_container, bg="#F5F5F5", width=380)
        self.left_panel.pack(side="left", fill="y", padx=(0, 15))
        self.left_panel.pack_propagate(False)
        self._build_sidebar()

        # 右侧显示区
        self.right_panel = ProfessionalCard(self.main_container, title="3D 可视化预览",
                                            subtitle="STL 模型与抛光路径生成")
        self.right_panel.pack(side="right", fill="both", expand=True)
        self._build_display_area()

    def _build_sidebar(self):
        """构建左侧控制卡片堆栈"""
        # 模型文件卡片
        file_card = ProfessionalCard(self.left_panel, title="模型文件", subtitle="导入分析")
        file_card.pack(fill="x", pady=(0, 15))

        tk.Entry(file_card.body_frame, textvariable=self.file_path_var, font=("微软雅黑", 9)).pack(fill="x", pady=5)
        ProfessionalButton(file_card.body_frame, text="选择模型文件",
                           command=self._on_browse, variant="ghost").pack(fill="x")
        ProfessionalButton(file_card.body_frame, text="加载并分析几何体",
                           command=self._on_load).pack(fill="x", pady=(8, 0))

        # 机器人配置
        robot_card = ProfessionalCard(self.left_panel, title="机器人配置")
        robot_card.pack(fill="x", pady=(0, 15))
        ttk.Combobox(robot_card.body_frame, textvariable=self.robot_model_var,
                     values=["IRB 2600", "IRB 4600", "IRB 6700"]).pack(fill="x")

        # 生成按钮
        ProfessionalButton(self.left_panel, text="🚀 生成 RAPID 代码",
                           command=self._on_generate, variant="secondary").pack(fill="x", side="bottom", pady=10)

    def _build_display_area(self):
        """右侧 3D 显示或日志区域"""
        self.log_area = tk.Text(self.right_panel.body_frame, bg="#1E1E1E", fg="#D4D4D4",
                                font=("Consolas", 10), relief="flat")
        self.log_area.pack(fill="both", expand=True)
        self.write_log("系统就绪，等待导入 STL 模型...")

    # --- 事件处理方法 ---
    def _on_browse(self):
        path = filedialog.askopenfilename(filetypes=[("STL Files", "*.stl")])
        if path: self.file_path_var.set(path)

    def _on_load(self):
        self.write_log(f"正在分析模型: {self.file_path_var.get()}...")
        # 实际逻辑会调用 self.core.load_model()

    def _on_generate(self):
        messagebox.showinfo("提示", "正在调用 Generators 模块生成 RAPID 代码...")

    def write_log(self, msg):
        self.log_area.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.see(tk.END)



if __name__ == "__main__":
    # 简单的本地测试入口
    root = tk.Tk()
    app = PolishingStudioGUI(root)
    root.mainloop()
