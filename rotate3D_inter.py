import taichi as ti
import math

ti.init(arch=ti.cpu)

vertices = ti.Vector.field(3, dtype=ti.f32, shape=8)
screen_coords1 = ti.Vector.field(2, dtype=ti.f32, shape=8)
screen_coords2 = ti.Vector.field(2, dtype=ti.f32, shape=8)

h_edges = [
    ((0, 1), 0xFF0000), ((1, 2), 0xFF0000), ((2, 3), 0xFF0000), ((3, 0), 0xFF0000),
    ((4, 5), 0x00FF00), ((5, 6), 0x00FF00), ((6, 7), 0x00FF00), ((7, 4), 0x00FF00),
    ((0, 4), 0x0000FF), ((1, 5), 0x0000FF), ((2, 6), 0x0000FF), ((3, 7), 0x0000FF)
]

@ti.func
def lerp(a: ti.f32, b: ti.f32, t: ti.f32):
    return a + t * (b - a)

@ti.func
def get_model_matrix(angle_x: ti.f32, angle_y: ti.f32, angle_z: ti.f32, trans_x: ti.f32, trans_y: ti.f32):
    rad_x = angle_x * math.pi / 180.0
    c_x = ti.cos(rad_x)
    s_x = ti.sin(rad_x)
    M_x = ti.Matrix([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, c_x, -s_x, 0.0],
        [0.0, s_x, c_x, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    
    rad_y = angle_y * math.pi / 180.0
    c_y = ti.cos(rad_y)
    s_y = ti.sin(rad_y)
    M_y = ti.Matrix([
        [c_y, 0.0, s_y, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s_y, 0.0, c_y, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    
    rad_z = angle_z * math.pi / 180.0
    c_z = ti.cos(rad_z)
    s_z = ti.sin(rad_z)
    M_z = ti.Matrix([
        [c_z, -s_z, 0.0, 0.0],
        [s_z, c_z, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    
    M_scale = ti.Matrix([
        [0.4, 0.0, 0.0, 0.0],
        [0.0, 0.4, 0.0, 0.0],
        [0.0, 0.0, 0.4, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    
    M_trans = ti.Matrix([
        [1.0, 0.0, 0.0, trans_x],
        [0.0, 1.0, 0.0, trans_y],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    
    return M_trans @ M_scale @ M_z @ M_y @ M_x

@ti.func
def get_view_matrix(eye_pos):
    return ti.Matrix([
        [1.0, 0.0, 0.0, -eye_pos[0]],
        [0.0, 1.0, 0.0, -eye_pos[1]],
        [0.0, 0.0, 1.0, -eye_pos[2]],
        [0.0, 0.0, 0.0, 1.0]
    ])

@ti.func
def get_projection_matrix(eye_fov: ti.f32, aspect_ratio: ti.f32, zNear: ti.f32, zFar: ti.f32):
    n = -zNear
    f = -zFar
    
    fov_rad = eye_fov * math.pi / 180.0
    t = ti.tan(fov_rad / 2.0) * ti.abs(n)
    b = -t
    r = aspect_ratio * t
    l = -r
    
    M_p2o = ti.Matrix([
        [n, 0.0, 0.0, 0.0],
        [0.0, n, 0.0, 0.0],
        [0.0, 0.0, n + f, -n * f],
        [0.0, 0.0, 1.0, 0.0]
    ])
    
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
    return M_ortho @ M_p2o

@ti.kernel
def compute_transform(angle_x: ti.f32, angle_y: ti.f32, angle_z: ti.f32, 
                       trans_x: ti.f32, trans_y: ti.f32,
                       screen_coords_out: ti.template()):
    eye_pos = ti.Vector([0.0, 0.0, 5.0])
    model = get_model_matrix(angle_x, angle_y, angle_z, trans_x, trans_y)
    view = get_view_matrix(eye_pos)
    proj = get_projection_matrix(45.0, 1.0, 0.1, 50.0)
    
    mvp = proj @ view @ model
    
    for i in range(8):
        v = vertices[i]
        v4 = ti.Vector([v[0], v[1], v[2], 1.0])
        v_clip = mvp @ v4
        v_ndc = v_clip / v_clip[3]
        screen_coords_out[i][0] = (v_ndc[0] + 1.0) / 2.0
        screen_coords_out[i][1] = (v_ndc[1] + 1.0) / 2.0

def main():
    vertices[0] = [1.0, 1.0, 1.0]
    vertices[1] = [-1.0, 1.0, 1.0]
    vertices[2] = [-1.0, -1.0, 1.0]
    vertices[3] = [1.0, -1.0, 1.0]
    vertices[4] = [1.0, 1.0, -1.0]
    vertices[5] = [-1.0, 1.0, -1.0]
    vertices[6] = [-1.0, -1.0, -1.0]
    vertices[7] = [1.0, -1.0, -1.0]
    
    gui = ti.GUI("Two Cubes Rotation Interpolation", res=(900, 900))
    
    cube1_x, cube1_y, cube1_z = 0.0, 0.0, 0.0
    cube1_tx, cube1_ty = -1.8, 0.0
    
    cube2_x, cube2_y, cube2_z = 60.0, 120.0, 45.0
    cube2_tx, cube2_ty = 1.8, 0.0
    
    t = 0.0
    direction = 1
    speed = 0.004
    
    while gui.running:
        if gui.get_event(ti.GUI.PRESS):
            if gui.event.key == ' ':
                direction *= -1
            elif gui.event.key == 'r':
                t = 0.0
                direction = 1
            elif gui.event.key == ti.GUI.ESCAPE:
                gui.running = False
        
        t += speed * direction
        if t > 1.0:
            t = 1.0
            direction = -1
        if t < 0.0:
            t = 0.0
            direction = 1
        
        current_x = cube1_x + t * (cube2_x - cube1_x)
        current_y = cube1_y + t * (cube2_y - cube1_y)
        current_z = cube1_z + t * (cube2_z - cube1_z)
        current_tx = cube1_tx + t * (cube2_tx - cube1_tx)
        current_ty = cube1_ty + t * (cube2_ty - cube1_ty)
        
        compute_transform(cube1_x, cube1_y, cube1_z, cube1_tx, cube1_ty, screen_coords1)
        compute_transform(cube2_x, cube2_y, cube2_z, cube2_tx, cube2_ty, screen_coords2)
        
        for edge_info in h_edges:
            edge, color = edge_info
            
            a1 = screen_coords1[edge[0]]
            b1 = screen_coords1[edge[1]]
            a2 = screen_coords2[edge[0]]
            b2 = screen_coords2[edge[1]]
            
            gui.line(a1, b1, radius=2, color=color)
            gui.line(a2, b2, radius=2, color=color)
            
            if 0.05 < t < 0.95:
                a_mid_x = a1[0] + t * (a2[0] - a1[0])
                a_mid_y = a1[1] + t * (a2[1] - a1[1])
                b_mid_x = b1[0] + t * (b2[0] - b1[0])
                b_mid_y = b1[1] + t * (b2[1] - b1[1])
                gui.line((a_mid_x, a_mid_y), (b_mid_x, b_mid_y), radius=2, color=0xFFFFFF)
        
        for i in range(8):
            pos1 = screen_coords1[i]
            pos2 = screen_coords2[i]
            if 0.05 < t < 0.95:
                mid_x = pos1[0] + t * (pos2[0] - pos1[0])
                mid_y = pos1[1] + t * (pos2[1] - pos1[1])
                gui.circle((mid_x, mid_y), radius=5, color=0xFFFFFF)
        
        gui.text(f"t = {t:.2f}", pos=(0.05, 0.95), color=0xFFFFFF, font_size=24)
        gui.text("SPACE: toggle direction, R: reset", pos=(0.05, 0.90), color=0xFFFFFF, font_size=18)
        gui.text("Cube 1", pos=(0.05, 0.85), color=0xFFFF00, font_size=16)
        gui.text("Cube 2", pos=(0.05, 0.80), color=0x00FFFF, font_size=16)
        gui.text("White: interpolation", pos=(0.05, 0.75), color=0xFFFFFF, font_size=16)
        
        gui.show()

if __name__ == '__main__':
    main()
