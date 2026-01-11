import os
import struct
import re
import numpy as np
import warnings
from typing import Dict, List, Any, Optional, Tuple

# 尝试导入科学计算库，处理依赖缺失情况
try:
    import trimesh
    from scipy.spatial import cKDTree

    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False
    print("Core Warning: trimesh or scipy not installed. 3D features will be limited.")


# 假设 AppConfig 从 utils 导入，或者在这里定义默认值
# from utils.config import AppConfig

class PolishingMathematicalModel:
    """
    抛光数学模型类
    负责核心的物理计算和几何分析算法
    """

    @staticmethod
    def calculate_surface_curvature(mesh, k_neighbors=10) -> np.ndarray:
        """计算网格顶点的表面曲率"""
        if not TRIMESH_AVAILABLE or mesh is None:
            return np.array([])

        vertices = mesh.vertices
        curvatures = []

        # 构建KD树用于快速查找邻居
        tree = cKDTree(vertices)

        for point in vertices:
            # 查找最近邻点
            distances, indices = tree.query(point, k=k_neighbors + 1)
            neighbors = vertices[indices[1:]]  # 排除自身

            # 计算PCA (主成分分析)
            if len(neighbors) >= 3:
                centered = neighbors - neighbors.mean(axis=0)
                cov_matrix = centered.T @ centered
                eigenvalues, _ = np.linalg.eigh(cov_matrix)

                # 特征值排序（升序）
                eigenvalues = eigenvalues[np.argsort(eigenvalues)]

                # 简化曲率估算: 最小特征值与最大特征值的比率
                if eigenvalues[2] > 0:
                    curvature = eigenvalues[0] / eigenvalues[2]
                    curvatures.append(curvature)
                else:
                    curvatures.append(0)
            else:
                curvatures.append(0)

        return np.array(curvatures)

    @staticmethod
    def calculate_contact_pressure(tool_radius, force, curvature):
        """基于Hertz接触理论计算接触压力"""
        if curvature <= 0:
            return force / (np.pi * tool_radius ** 2)

        effective_radius = 1 / curvature if curvature != 0 else tool_radius
        # 简化模型：假设弹性模量为钢 (210GPa)
        contact_radius = np.cbrt(3 * force * effective_radius / (4 * 210e9))

        if contact_radius == 0:
            return 0

        max_pressure = 1.5 * force / (np.pi * contact_radius ** 2)
        return max_pressure

    @staticmethod
    def calculate_tool_orientation(normal):
        """将法向量转换为工具姿态 (四元数 [qw, qx, qy, qz])"""
        # 归一化
        normal = normal / np.linalg.norm(normal)

        # 默认Z轴朝上
        up_vector = np.array([0, 0, 1])

        if np.allclose(normal, up_vector) or np.allclose(normal, -up_vector):
            axis = np.array([1, 0, 0])
        else:
            axis = np.cross(up_vector, normal)
            axis = axis / np.linalg.norm(axis)

        angle = np.arccos(np.clip(np.dot(up_vector, normal), -1.0, 1.0))

        qw = np.cos(angle / 2)
        qx = axis[0] * np.sin(angle / 2)
        qy = axis[1] * np.sin(angle / 2)
        qz = axis[2] * np.sin(angle / 2)

        return [qw, qx, qy, qz]

    @staticmethod
    def optimize_path_sequence(points):
        """
        路径点序列优化 (简化版 TSP - 旅行商问题)
        使用最近邻算法减少空行程
        """
        if len(points) <= 2:
            return points

        # 转换为 numpy 数组以便计算
        points_np = np.array(points)

        current_idx = 0
        visited = [False] * len(points)
        visited[current_idx] = True
        optimized_indices = [0]

        for _ in range(len(points) - 1):
            min_dist = float('inf')
            next_idx = -1

            # 这里为了性能简化了搜索，实际生产中可能需要 KDTree 加速
            current_pos = points_np[current_idx]

            for i in range(len(points)):
                if not visited[i]:
                    # 欧几里得距离
                    dist = np.linalg.norm(current_pos - points_np[i])
                    if dist < min_dist:
                        min_dist = dist
                        next_idx = i

            if next_idx != -1:
                visited[next_idx] = True
                optimized_indices.append(next_idx)
                current_idx = next_idx

        return [points[i] for i in optimized_indices]


class NXSTLProcessor:
    """
    NX STL 文件处理器
    专门用于处理 Siemens NX 导出的 STL 文件及其特定的头部元数据
    """

    @staticmethod
    def read_metadata(file_path: str) -> Dict[str, Any]:
        """读取文件头部的元数据"""
        metadata = {
            'is_nx': False,
            'units': 'mm',
            'original_format': 'STL',
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            'nx_specific': {}
        }

        try:
            with open(file_path, 'rb') as f:
                header_bytes = f.read(84)  # 标准STL头80字节+4字节面数
                header_str = header_bytes[:80].decode('ascii', errors='ignore')

                # 检测 NX 标识
                nx_indicators = ['NX', 'Siemens', 'UG', 'Unigraphics', 'UNITS=', 'CREATED=']
                if any(ind in header_str for ind in nx_indicators):
                    metadata['is_nx'] = True
                    metadata['original_format'] = 'NX STL'

                    # 解析 NX 特有字段
                    if 'MM' in header_str.upper():
                        metadata['units'] = 'mm'
                    elif 'IN' in header_str.upper():
                        metadata['units'] = 'inch'

                    # 提取创建日期
                    date_match = re.search(r'CREATED=([0-9\-/]+)', header_str, re.IGNORECASE)
                    if date_match:
                        metadata['creation_date'] = date_match.group(1)

                    # 提取零件名
                    part_match = re.search(r'PART=(.+)', header_str, re.IGNORECASE)
                    if part_match:
                        metadata['part_name'] = part_match.group(1).strip()

        except Exception as e:
            print(f"Core Error: Failed to read STL metadata: {e}")

        return metadata

    @staticmethod
    def load_mesh(file_path: str, force_nx_processing=False):
        """加载网格并应用单位转换"""
        if not TRIMESH_AVAILABLE:
            raise ImportError("Core dependency 'trimesh' is missing.")

        metadata = NXSTLProcessor.read_metadata(file_path)
        mesh = trimesh.load(file_path)

        # 单位标准化为 mm
        if force_nx_processing or metadata.get('is_nx'):
            if metadata['units'] == 'inch':
                mesh.vertices *= 25.4
            elif metadata['units'] == 'm':
                mesh.vertices *= 1000

        # 将元数据附加到 mesh 对象
        mesh.metadata.update(metadata)
        return mesh


class AdvancedPathPlanner:
    """
    高级路径规划器
    """

    def __init__(self, mesh, tool_diameter=8.0):
        self.mesh = mesh
        self.tool_radius = tool_diameter / 2.0
        self.vertices = mesh.vertices if mesh else []

    def generate_paths(self, strategy: str, **kwargs) -> List[Dict]:
        """通用路径生成入口"""
        if self.mesh is None:
            return []

        if strategy == "adaptive":
            stepover = kwargs.get('stepover', 0.5)
            return self._generate_adaptive_path(stepover)
        elif strategy == "parallel":
            angle = kwargs.get('angle', 0)
            spacing = kwargs.get('spacing', self.tool_radius * 0.7)
            return self._generate_parallel_path(angle, spacing)
        else:
            return []

    def _generate_adaptive_path(self, stepover_ratio):
        """自适应切片路径生成"""
        # 计算 Z 轴范围
        min_z, max_z = np.min(self.vertices[:, 2]), np.max(self.vertices[:, 2])
        step_size = self.tool_radius * stepover_ratio

        paths = []
        # 按 Z 轴分层切片 (简化算法，实际应使用 trimesh.intersections.mesh_plane)
        # 这里为了保持与原代码逻辑一致，使用顶点筛选法

        # 计算曲率用于排序
        curvatures = PolishingMathematicalModel.calculate_surface_curvature(self.mesh)

        for z in np.arange(min_z, max_z, step_size):
            # 筛选当前层附近的点
            mask = (self.vertices[:, 2] >= z) & (self.vertices[:, 2] < z + step_size)
            if not np.any(mask):
                continue

            layer_points = self.vertices[mask]

            # 如果有曲率数据，可以基于曲率对点进行优先级排序或过滤
            # 此处进行简单的路径点排序优化
            optimized_points = PolishingMathematicalModel.optimize_path_sequence(layer_points.tolist())

            paths.append({
                'type': 'adaptive_layer',
                'z_level': float(z),
                'points': optimized_points
            })

        return paths

    def _generate_parallel_path(self, angle, spacing):
        """平行线路径生成"""
        # 获取包围盒
        min_coords = np.min(self.vertices, axis=0)
        max_coords = np.max(self.vertices, axis=0)

        paths = []

        if angle == 0:  # X 方向扫描
            for y in np.arange(min_coords[1], max_coords[1], spacing):
                line_points = []
                # 简单的投影查找: 寻找 Y 坐标接近的点
                # 实际生产中应使用射线投射 (Ray Casting)
                mask = np.abs(self.vertices[:, 1] - y) < (spacing / 2.0)
                if np.any(mask):
                    points_strip = self.vertices[mask]
                    # 按 X 排序
                    points_strip = points_strip[points_strip[:, 0].argsort()]
                    line_points = points_strip.tolist()

                if line_points:
                    paths.append({'points': line_points, 'type': 'parallel_x'})

        # Y 方向同理...
        return paths


class PolishingCore:
    """
    核心业务引擎 (Facade Pattern)
    GUI 应该只与这个类交互，而不是直接调用底层的 Processor 或 Model
    """

    def __init__(self):
        self.current_mesh = None
        self.mesh_metadata = {}
        self.generated_paths = {}  # 存储生成的路径数据

        # 默认参数
        self.params = {
            'tool_diameter': 8.0,
            'rough_speed': 300,
            'fine_speed': 200,
            'safety_height': 50.0
        }

    def load_model(self, file_path: str, force_nx=True) -> Tuple[bool, str, Dict]:
        """加载模型并返回摘要信息"""
        if not os.path.exists(file_path):
            return False, "File not found", {}

        try:
            self.current_mesh = NXSTLProcessor.load_mesh(file_path, force_nx)
            self.mesh_metadata = self.current_mesh.metadata

            # 简单的统计信息
            stats = {
                'vertices': len(self.current_mesh.vertices),
                'faces': len(self.current_mesh.faces),
                'bounds': self.current_mesh.bounds.tolist() if self.current_mesh.bounds is not None else [],
                'is_nx': self.mesh_metadata.get('is_nx', False)
            }
            return True, "Model loaded successfully", stats

        except Exception as e:
            return False, str(e), {}

    def analyze_geometry(self) -> Dict[str, Any]:
        """执行几何分析"""
        if self.current_mesh is None:
            return {}

        # 计算曲率
        curvatures = PolishingMathematicalModel.calculate_surface_curvature(self.current_mesh)
        avg_curvature = np.mean(curvatures) if len(curvatures) > 0 else 0

        return {
            'avg_curvature': float(avg_curvature),
            'max_curvature': float(np.max(curvatures)) if len(curvatures) > 0 else 0,
            'volume': getattr(self.current_mesh, 'volume', 0),
            'area': getattr(self.current_mesh, 'area', 0)
        }

    def generate_polishing_paths(self, config: Dict) -> Dict[str, List]:
        """
        生成路径数据
        config: 包含 path_type, stepover 等参数
        """
        if self.current_mesh is None:
            raise ValueError("No model loaded")

        planner = AdvancedPathPlanner(self.current_mesh, config.get('tool_diameter', 8.0))

        # 1. 生成粗抛路径
        rough_paths = planner.generate_paths(
            config.get('path_type', 'adaptive'),
            stepover=config.get('stepover', 0.5)
        )

        # 2. 生成精抛路径 (通常步距更小，或者方向不同)
        fine_paths = planner.generate_paths(
            'parallel',  # 假设精抛默认平行线
            angle=90,
            spacing=config.get('tool_diameter', 8.0) * 0.3
        )

        # 存储结果，用于后续生成代码
        # 我们需要将原始点数据转换为带有法向量和速度信息的结构化数据
        self.generated_paths = {
            'rough': self._enrich_path_data(rough_paths, 'rough', config),
            'fine': self._enrich_path_data(fine_paths, 'fine', config)
        }

        return self.generated_paths

    def _enrich_path_data(self, raw_paths: List[Dict], stage: str, config: Dict) -> List[Dict]:
        """
        将纯几何路径点转换为包含工艺参数（速度、区域、姿态）的完整数据
        供 Generator 模块使用
        """
        enriched_paths = []
        speed = config.get(f'{stage}_speed', 200)

        for idx, path_segment in enumerate(raw_paths):
            points = path_segment['points']
            enriched_points = []

            for pt in points:
                # 简单法向量：垂直向上 (Z+)，实际应计算 mesh 最近面片的法向量
                normal = [0, 0, 1]
                orientation = PolishingMathematicalModel.calculate_tool_orientation(normal)

                enriched_points.append({
                    'pos': pt,  # [x, y, z]
                    'orient': orientation,  # [q1, q2, q3, q4]
                    'speed': speed
                })

            if enriched_points:
                enriched_paths.append({
                    'id': idx,
                    'name': f"{stage}_{idx}",
                    'points': enriched_points
                })

        return enriched_paths

    def get_generated_code_data(self) -> Dict:
        """获取用于生成器的数据包"""
        return {
            'paths': self.generated_paths,
            'metadata': self.mesh_metadata,
            'params': self.params
        }