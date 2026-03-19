import taichi as ti
import math

# 初始化 Taichi，指定使用 CPU 后端
ti.init(arch=ti.cpu)

# 声明 Taichi 的 Field 来存储顶点和转换后的屏幕坐标
vertices = ti.Vector.field(3, dtype=ti.f32, shape=8)  # 8 个顶点
screen_coords = ti.Vector.field(2, dtype=ti.f32, shape=8)  # 8 个屏幕坐标

# 定义立方体的 12 条边及其颜色
h_edges = [
    ((0, 1), 0xFF0000), ((1, 2), 0xFF0000), ((2, 3), 0xFF0000), ((3, 0), 0xFF0000),  # 前面 - 红色
    ((4, 5), 0x00FF00), ((5, 6), 0x00FF00), ((6, 7), 0x00FF00), ((7, 4), 0x00FF00),  # 后面 - 绿色
    ((0, 4), 0x0000FF), ((1, 5), 0x0000FF), ((2, 6), 0x0000FF), ((3, 7), 0x0000FF)   # 连接前后 - 蓝色
]

@ti.func
def get_model_matrix(angle_x: ti.f32, angle_y: ti.f32, angle_z: ti.f32):
    """
    模型变换矩阵：绕 X、Y、Z 轴旋转并平移
    """
    # 绕 X 轴旋转
    rad_x = angle_x * math.pi / 180.0
    c_x = ti.cos(rad_x)
    s_x = ti.sin(rad_x)
    M_x = ti.Matrix([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, c_x, -s_x, 0.0],
        [0.0, s_x, c_x, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    
    # 绕 Y 轴旋转
    rad_y = angle_y * math.pi / 180.0
    c_y = ti.cos(rad_y)
    s_y = ti.sin(rad_y)
    M_y = ti.Matrix([
        [c_y, 0.0, s_y, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s_y, 0.0, c_y, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    
    # 绕 Z 轴旋转
    rad_z = angle_z * math.pi / 180.0
    c_z = ti.cos(rad_z)
    s_z = ti.sin(rad_z)
    M_z = ti.Matrix([
        [c_z, -s_z, 0.0, 0.0],
        [s_z, c_z, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    
    # 平移矩阵：向右上方移动
    M_trans = ti.Matrix([
        [1.0, 0.0, 0.0, 2.0],  # 向右移动 1.5 个单位
        [0.0, 1.0, 0.0, 2.0],  # 向上移动 1.5 个单位
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    
    # 组合变换矩阵（先旋转，后平移）
    return M_trans @ M_z @ M_y @ M_x

@ti.func
def get_view_matrix(eye_pos):
    """
    视图变换矩阵：将相机移动到原点
    """
    return ti.Matrix([
        [1.0, 0.0, 0.0, -eye_pos[0]],
        [0.0, 1.0, 0.0, -eye_pos[1]],
        [0.0, 0.0, 1.0, -eye_pos[2]],
        [0.0, 0.0, 0.0, 1.0]
    ])

@ti.func
def get_projection_matrix(eye_fov: ti.f32, aspect_ratio: ti.f32, zNear: ti.f32, zFar: ti.f32):
    """
    透视投影矩阵
    """
    # 视线看向 -Z 轴，实际坐标为负
    n = -zNear
    f = -zFar
    
    # 视角转化为弧度并求出 t, b, r, l
    fov_rad = eye_fov * math.pi / 180.0
    t = ti.tan(fov_rad / 2.0) * ti.abs(n)
    b = -t
    r = aspect_ratio * t
    l = -r
    
    # 1. 挤压矩阵: 透视平截头体 -> 长方体
    M_p2o = ti.Matrix([
        [n, 0.0, 0.0, 0.0],
        [0.0, n, 0.0, 0.0],
        [0.0, 0.0, n + f, -n * f],
        [0.0, 0.0, 1.0, 0.0]
    ])
    
    # 2. 正交投影矩阵: 缩放与平移至 [-1, 1]^3
    M_ortho_scale = ti.Matrix([
        [2.0 / (r - l), 0.0, 0.0, 0.0],
        [0.0, 2.0 / (t - b), 0.0, 0.0],
        [0.0, 0.0, 2.0 / (n - f), 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    
    M_ortho_trans = ti.Matrix([
        [1.0, 0.0, 0.0, -(r + l) / 2.0],
        [0.0, 1.0, 0.0, -(t + b) / 2.0],
        [0.0, 0.0, 1.0, -(n + f) / 2.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    
    M_ortho = M_ortho_scale @ M_ortho_trans
    
    # 返回组合矩阵
    return M_ortho @ M_p2o

@ti.kernel
def compute_transform(angle_x: ti.f32, angle_y: ti.f32, angle_z: ti.f32):
    """
    在并行架构上计算顶点的坐标变换
    """
    eye_pos = ti.Vector([2.0, 2.0, 5.0])  # 调整相机位置，获得更好的视角
    model = get_model_matrix(angle_x, angle_y, angle_z)
    view = get_view_matrix(eye_pos)
    proj = get_projection_matrix(45.0, 1.0, 0.1, 50.0)
    
    # MVP 矩阵：右乘原则
    mvp = proj @ view @ model
    
    for i in range(8):
        v = vertices[i]
        # 补全齐次坐标
        v4 = ti.Vector([v[0], v[1], v[2], 1.0])
        v_clip = mvp @ v4
        
        # 透视除法，转化为 NDC 坐标 [-1, 1]
        v_ndc = v_clip / v_clip[3]
        
        # 视口变换：映射到 GUI 的 [0, 1] x [0, 1] 空间
        screen_coords[i][0] = (v_ndc[0] + 1.0) / 2.0
        screen_coords[i][1] = (v_ndc[1] + 1.0) / 2.0

def main():
    # 初始化立方体顶点，中心在原点，边长为 2
    vertices[0] = [1.0, 1.0, 1.0]    # 前右上
    vertices[1] = [-1.0, 1.0, 1.0]   # 前左上
    vertices[2] = [-1.0, -1.0, 1.0]  # 前左下
    vertices[3] = [1.0, -1.0, 1.0]   # 前右下
    vertices[4] = [1.0, 1.0, -1.0]   # 后右上
    vertices[5] = [-1.0, 1.0, -1.0]  # 后左上
    vertices[6] = [-1.0, -1.0, -1.0] # 后左下
    vertices[7] = [1.0, -1.0, -1.0]  # 后右下
    
    # 创建 GUI 窗口
    gui = ti.GUI("3D Cube Transformation (Taichi)", res=(700, 700))
    angle_x = 0.0
    angle_y = 0.0
    angle_z = 0.0
    
    while gui.running:
        if gui.get_event(ti.GUI.PRESS):
            if gui.event.key == 'a':
                angle_y += 10.0  # 绕 Y 轴旋转
            elif gui.event.key == 'd':
                angle_y -= 10.0  # 绕 Y 轴旋转
            elif gui.event.key == 'w':
                angle_x += 10.0  # 绕 X 轴旋转
            elif gui.event.key == 's':
                angle_x -= 10.0  # 绕 X 轴旋转
            elif gui.event.key == 'q':
                angle_z += 10.0  # 绕 Z 轴旋转
            elif gui.event.key == 'e':
                angle_z -= 10.0  # 绕 Z 轴旋转
            elif gui.event.key == ti.GUI.ESCAPE:
                gui.running = False
        
        # 自动旋转，增强三维效果
        angle_x += 0.5
        angle_y += 0.8
        
        # 计算变换
        compute_transform(angle_x, angle_y, angle_z)
        
        # 绘制立方体的 12 条边
        for edge_info in h_edges:
            edge, color = edge_info
            a = screen_coords[edge[0]]
            b = screen_coords[edge[1]]
            gui.line(a, b, radius=2, color=color)
        
        gui.show()

if __name__ == '__main__':
    main()
