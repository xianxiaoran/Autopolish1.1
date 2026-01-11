import tkinter as tk
from Utils.theme import UIColors


class ProfessionalFrame(tk.Frame):
    """基础专业框架 - 提供统一的边距管理"""

    def __init__(self, parent, padding=16, bg=UIColors.BG_MAIN, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.padding = padding


class ProfessionalCard(tk.Frame):
    """
    工业级卡片容器
    包含：标题栏、副标题、内容主体、阴影边框效果
    """

    def __init__(self, parent, title="", subtitle="", padding=16, bg=UIColors.BG_LIGHT, **kwargs):
        super().__init__(parent, bg=UIColors.BORDER, **kwargs)  # 使用边框色作为最底层

        # 内容容器（实现 1px 边框效果）
        self.content_frame = tk.Frame(self, bg=bg)
        self.content_frame.pack(fill="both", expand=True, padx=1, pady=1)

        # 标题栏区域
        if title:
            self.title_frame = tk.Frame(self.content_frame, bg="#F8F9FA", height=40)
            self.title_frame.pack(fill="x")
            self.title_frame.pack_propagate(False)

            # 主标题
            tk.Label(
                self.title_frame,
                text=title,
                font=("微软雅黑", 10, "bold"),
                bg="#F8F9FA",
                fg=UIColors.TEXT_PRIMARY
            ).pack(side="left", padx=padding)

            # 副标题
            if subtitle:
                tk.Label(
                    self.title_frame,
                    text=subtitle,
                    font=("微软雅黑", 8),
                    bg="#F8F9FA",
                    fg=UIColors.TEXT_HINT
                ).pack(side="right", padx=padding)

            # 分割线
            tk.Frame(self.content_frame, bg=UIColors.BORDER, height=1).pack(fill="x")

        # 内容主体区
        self.body_frame = tk.Frame(self.content_frame, bg=bg)
        self.body_frame.pack(fill="both", expand=True, padx=padding, pady=padding)


class ProfessionalButton(tk.Frame):
    """
    带交互反馈的专业按钮
    variant 可选: 'primary' (蓝色), 'secondary' (绿色), 'ghost' (白色)
    """

    def __init__(self, parent, text="", command=None, variant="primary", **kwargs):
        super().__init__(parent, **kwargs)

        # 根据变体选择颜色方案
        styles = {
            "primary": {"bg": UIColors.PRIMARY, "fg": "white", "hover": UIColors.PRIMARY_HOVER},
            "secondary": {"bg": UIColors.SUCCESS, "fg": "white", "hover": "#05A84E"},
            "ghost": {"bg": "white", "fg": UIColors.TEXT_PRIMARY, "hover": "#F5F5F5"}
        }
        self.style = styles.get(variant, styles["primary"])

        self.btn_frame = tk.Frame(self, bg=self.style["bg"], cursor="hand2")
        self.btn_frame.pack(fill="both", expand=True)

        self.label = tk.Label(
            self.btn_frame,
            text=text,
            fg=self.style["fg"],
            bg=self.style["bg"],
            font=("微软雅黑", 9, "bold"),
            pady=8
        )
        self.label.pack()

        # 绑定悬停与点击事件
        for item in [self.btn_frame, self.label]:
            item.bind("<Enter>", self._on_enter)
            item.bind("<Leave>", self._on_leave)
            item.bind("<Button-1>", lambda e: self._on_click(command))

    def _on_enter(self, e):
        self.btn_frame.config(bg=self.style["hover"])
        self.label.config(bg=self.style["hover"])

    def _on_leave(self, e):
        self.btn_frame.config(bg=self.style["bg"])
        self.label.config(bg=self.style["bg"])

    def _on_click(self, command):
        if command:
            command()


class LogTerminal(tk.Frame):
    """
    专用的日志终端组件
    带有自动滚动和时间戳格式化功能
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=UIColors.BG_DARK, **kwargs)

        self.text_area = tk.Text(
            self,
            bg=UIColors.BG_DARK,
            fg=UIColors.TEXT_CODE,
            font=("Consolas", 10),
            padx=10,
            pady=10,
            relief="flat",
            insertbackground="white"  # 光标颜色
        )

        self.scrollbar = tk.Scrollbar(self, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.text_area.pack(side="left", fill="both", expand=True)

    def append(self, message, level="INFO"):
        """向终端添加一条消息"""
        from datetime import datetime
        time_str = datetime.now().strftime("%H:%M:%S")

        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, f"[{time_str}] ", "time")

        color = UIColors.TEXT_CODE
        if level == "ERROR":
            color = UIColors.ERROR
        elif level == "WARNING":
            color = UIColors.WARNING

        self.text_area.insert(tk.END, f"{message}\n", level)
        self.text_area.tag_config("time", foreground="#6A9955")  # 绿色时间戳
        self.text_area.tag_config("ERROR", foreground=UIColors.ERROR)

        self.text_area.config(state="disabled")
        self.text_area.see(tk.END)