class UIColors:
    """
    专业 UI 配色方案
    基于原 ProfessionalColors 类简化
    """

    # 品牌主色 (ABB Blue)
    PRIMARY = "#005596"
    PRIMARY_HOVER = "#003D6B"
    PRIMARY_TEXT = "#FFFFFF"

    # 功能色
    SUCCESS = "#07C160"  # 绿色
    WARNING = "#FF9500"  # 橙色
    ERROR = "#FF4D4F"  # 红色
    INFO = "#1890FF"  # 蓝色

    # 背景色系
    BG_MAIN = "#F0F0F0"  # 主背景
    BG_LIGHT = "#FFFFFF"  # 卡片/容器背景
    BG_SIDEBAR = "#F5F5F5"  # 侧边栏
    BG_DARK = "#1E1E1E"  # 代码编辑器/日志背景

    # 文字色系
    TEXT_PRIMARY = "#333333"  # 主标题
    TEXT_SECONDARY = "#666666"  # 副标题/正文
    TEXT_HINT = "#999999"  # 提示文本
    TEXT_CODE = "#D4D4D4"  # 代码高亮

    # 边框
    BORDER = "#E0E0E0"

    @staticmethod
    def hex_to_rgb(hex_color):
        """辅助函数：Hex 转 RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))