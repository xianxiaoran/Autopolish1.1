import datetime
from typing import Dict, List, Any, Optional


class RAPIDTemplates:
    """
    存储 RAPID 代码的静态模板
    将数据结构与文本格式分离
    """
    MODULE_HEADER = """MODULE {module_name}
! ========================================================
! 生成时间: {timestamp}
! 生成器: ABB Polishing Studio v2.0
! 机器人: {robot_model}
! ========================================================"""

    TOOL_DATA = """
! 工具数据定义
CONST tooldata {tool_name} := [
    TRUE,
    [[0, 0, {tool_length:.1f}], [1, 0, 0, 0]],
    [{tool_mass:.3f}, [0, 0, {cg_z:.1f}], [1, 0, 0, 0], 0.001, 0.001, 0.001]
];"""

    WOBJ_DATA = """
! 工件坐标系定义
CONST wobjdata {wobj_name} := [
    FALSE, TRUE, "", [[0, 0, 0], [1, 0, 0, 0]],
    [[{x:.1f}, {y:.1f}, {z:.1f}], [{q1:.4f}, {q2:.4f}, {q3:.4f}, {q4:.4f}]]
];"""

    STANDARD_SPEEDS = """
! 标准速度定义
CONST speeddata vApproach := [100, 500, 5000, 1000];
CONST speeddata vRetract := [150, 500, 5000, 1000];
CONST speeddata vFast := [500, 1000, 5000, 1000];"""

    STANDARD_ZONES = """
! 标准区域定义
CONST zonedata zFine := [FALSE, 0.3, 0.3, 0.3, 0.03, 0.3, 0.3];
CONST zonedata zMedium := [FALSE, 1.0, 1.0, 1.0, 0.1, 1.0, 1.0];
CONST zonedata zLarge := [FALSE, 5.0, 5.0, 5.0, 0.3, 5.0, 5.0];"""

    IO_SIGNALS = """
! IO 信号声明
VAR signaldo doSpindleStart;
VAR signaldo doCoolantOn;
VAR signaldi diEmergencyStop;
VAR signaldi diToolInPlace;"""

    ROBTARGET = "CONST robtarget {name} := [[{x:.3f},{y:.3f},{z:.3f}],[{q1:.6f},{q2:.6f},{q3:.6f},{q4:.6f}],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];"


class AdvancedFeatures:
    """
    高级功能代码片段生成器
    对应原代码中的 AdvancedRAPIDFeatures
    """

    @staticmethod
    def get_force_control_logic(params: Dict) -> str:
        """生成力控制定义"""
        force = params.get('target_force', 30.0)
        return f"""
! --- 高级功能: 力控制 ---
CONST forcedata fPolishing := [1, [[0,0,0.1], [1,0,0,0]], 50, 50];
PROC ActivateForceControl()
    ForceDef fPolishing, [[0,0,{force}]], tPolishingTool;
    ForceAct fPolishing;
ENDPROC
PROC DeactivateForceControl()
    StopForce;
ENDPROC"""

    @staticmethod
    def get_error_recovery() -> str:
        """生成错误恢复逻辑"""
        return """
! --- 高级功能: 错误恢复 ---
PROC ErrorHandler()
    IF ERRNO = ERR_COLL_STOP THEN
        StopMove;
        MoveL RelTool(CRobT(), 0, 0, -10), vSlow, fine, tPolishingTool;
        ExitCycle;
    ENDIF
ENDPROC"""


class RAPIDGenerator:
    """
    工业级 RAPID 代码生成器
    接收 Core 模块处理后的数据，输出 .mod 文件内容
    """

    def __init__(self):
        self.code_buffer = []

    def generate(self, context: Dict) -> str:
        """
        主生成方法
        :param context: 包含 'paths', 'metadata', 'params' 的字典 (由 Core 提供)
        :return: 完整的 RAPID 代码字符串
        """
        self.code_buffer = []
        params = context.get('params', {})
        paths = context.get('paths', {})

        # 1. 模块头
        self._add_header(context)

        # 2. 数据声明 (Tool, Wobj, Speed, Zone, IO)
        self._add_data_declarations(params)

        # 3. 目标点定义 (Robtargets)
        self._add_robtargets(paths)

        # 4. 高级功能定义 (可选)
        if params.get('enable_force_control'):
            self.code_buffer.append(AdvancedFeatures.get_force_control_logic(params))

        # 5. 子程序定义 (Routine)
        self._add_procedures(paths, params)

        # 6. 主程序 (Main)
        self._add_main(paths, params)

        # 7. 模块结束
        self.code_buffer.append("ENDMODULE")

        return "\n".join(self.code_buffer)

    def _add_header(self, context):
        """生成模块头部注释"""
        header = RAPIDTemplates.MODULE_HEADER.format(
            module_name=context.get('program_name', 'Polishing_Module'),
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            robot_model=context.get('params', {}).get('robot_model', 'IRB 2600')
        )
        self.code_buffer.append(header)

    def _add_data_declarations(self, params):
        """生成数据声明"""
        # 工具
        tool_str = RAPIDTemplates.TOOL_DATA.format(
            tool_name="tPolishingTool",
            tool_length=params.get('tool_length', 200.0),
            tool_mass=0.5,
            cg_z=params.get('tool_length', 200.0) / 2
        )
        self.code_buffer.append(tool_str)

        # 工件坐标系 (默认零点)
        wobj_str = RAPIDTemplates.WOBJ_DATA.format(
            wobj_name="wWorkpiece", x=0, y=0, z=0, q1=1, q2=0, q3=0, q4=0
        )
        self.code_buffer.append(wobj_str)

        # 速度与区域
        self.code_buffer.append(RAPIDTemplates.STANDARD_SPEEDS)

        # 动态生成工艺速度
        r_speed = params.get('rough_speed', 300)
        f_speed = params.get('fine_speed', 200)
        self.code_buffer.append(f"CONST speeddata vRough := [{r_speed}, 500, 5000, 1000];")
        self.code_buffer.append(f"CONST speeddata vFine := [{f_speed}, 500, 5000, 1000];")

        self.code_buffer.append(RAPIDTemplates.STANDARD_ZONES)
        self.code_buffer.append(RAPIDTemplates.IO_SIGNALS)

    def _add_robtargets(self, paths):
        """将路径点转换为 const robtarget"""
        self.code_buffer.append("\n! --- 目标点定义 ---")

        # 遍历 'rough' 和 'fine' 阶段
        for stage_name, segments in paths.items():
            for segment in segments:
                points = segment.get('points', [])
                for i, pt in enumerate(points):
                    # 点命名规范: p_{stage}_{pathID}_{pointID}
                    # e.g., p_rough_0_001
                    p_name = f"p_{stage_name}_{segment['id']}_{i:03d}"

                    pos = pt['pos']
                    orient = pt['orient']

                    target_line = RAPIDTemplates.ROBTARGET.format(
                        name=p_name,
                        x=pos[0], y=pos[1], z=pos[2],
                        q1=orient[0], q2=orient[1], q3=orient[2], q4=orient[3]
                    )
                    self.code_buffer.append(target_line)

    def _add_procedures(self, paths, params):
        """生成具体的路径执行程序"""
        use_force = params.get('enable_force_control', False)

        for stage_name in ['rough', 'fine']:
            if stage_name not in paths:
                continue

            proc_name = f"Path_{stage_name}"
            speed_var = "vRough" if stage_name == 'rough' else "vFine"
            zone_var = "zMedium" if stage_name == 'rough' else "zFine"

            self.code_buffer.append(f"\nPROC {proc_name}()")
            self.code_buffer.append(f'    TPWrite "Executing {stage_name} polishing...";')

            if use_force:
                self.code_buffer.append("    ActivateForceControl;")

            segments = paths[stage_name]
            for segment in segments:
                points = segment.get('points', [])
                self.code_buffer.append(f"\n    ! Segment {segment['id']}")

                # 移动指令生成
                for i in range(len(points)):
                    p_name = f"p_{stage_name}_{segment['id']}_{i:03d}"
                    # MoveL pTarget, vSpeed, zZone, tool \WObj:=wobj;
                    line = f"    MoveL {p_name}, {speed_var}, {zone_var}, tPolishingTool \\WObj:=wWorkpiece;"
                    self.code_buffer.append(line)

            if use_force:
                self.code_buffer.append("    DeactivateForceControl;")

            self.code_buffer.append("ENDPROC")

    def _add_main(self, paths, params):
        """生成 main 程序"""
        self.code_buffer.append("\nPROC main()")
        self.code_buffer.append("    TPWrite \"Starting Polishing Cycle\";")
        self.code_buffer.append("    ! 初始化 IO")
        self.code_buffer.append("    SetDO doSpindleStart, 1;")
        self.code_buffer.append("    WaitTime 1;")

        if 'rough' in paths:
            self.code_buffer.append("    Path_rough;")

        if 'fine' in paths:
            self.code_buffer.append("    Path_fine;")

        self.code_buffer.append("    SetDO doSpindleStart, 0;")
        self.code_buffer.append("    TPWrite \"Cycle Complete\";")
        self.code_buffer.append("ENDPROC")