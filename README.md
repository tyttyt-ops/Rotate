# Rotate

## 仓库地址

本项目的 SSH 仓库地址为：
```
git@github.com:tyttyt-ops/Rotate.git
```

## 项目概述

Rotate 是一个使用 Taichi 库实现的 2D 和 3D 旋转示例项目，展示了如何通过矩阵变换实现几何体的旋转和透视投影。

## 功能特点

- **2D 旋转示例**：实现了一个三角形的旋转和透视投影
- **3D 旋转示例**：实现了一个彩色立方体的三维旋转和透视投影
- **交互式控制**：支持通过键盘控制几何体的旋转方向和角度
- **自动旋转**：3D 示例中添加了自动旋转功能，增强视觉效果
- **彩色渲染**：3D 立方体的不同面使用不同颜色渲染，增强立体感

## 安装依赖

本项目需要以下依赖：

- Python 3.7+
- Taichi 1.7.4+

可以通过以下命令安装依赖：

```bash
pip install taichi
```

## 使用方法

### 运行 2D 旋转示例

```bash
python rotate2D.py
```

### 运行 3D 旋转示例

```bash
python rotate3D.py
```

## 交互控制

### 2D 示例控制

- **A 键**：顺时针旋转
- **D 键**：逆时针旋转
- **ESC 键**：退出程序

### 3D 示例控制

- **A 键**：绕 Y 轴顺时针旋转
- **D 键**：绕 Y 轴逆时针旋转
- **W 键**：绕 X 轴顺时针旋转
- **S 键**：绕 X 轴逆时针旋转
- **Q 键**：绕 Z 轴顺时针旋转
- **E 键**：绕 Z 轴逆时针旋转
- **ESC 键**：退出程序

## 文件结构

```
.
├── README.md          # 项目说明文档
├── rotate2D.py        # 2D 旋转示例
└── rotate3D.py        # 3D 旋转示例
```

## 技术实现

### 矩阵变换

本项目使用了以下矩阵变换：

1. **模型变换矩阵**：实现几何体的旋转和平移
2. **视图变换矩阵**：将相机移动到原点
3. **透视投影矩阵**：将 3D 坐标投影到 2D 屏幕

### 渲染流程

1. 定义几何体顶点
2. 计算 MVP 矩阵（模型-视图-投影矩阵）
3. 对每个顶点应用 MVP 变换
4. 进行透视除法，转换为 NDC 坐标
5. 进行视口变换，映射到屏幕空间
6. 绘制几何体

## 示例效果

### 2D 示例
1.**A 键**：顺时针旋转&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;2.**D 键**：逆时针旋转

![3D Transformation (Taichi) (18 13 FPS) 2026-03-23 23-01-25](https://github.com/user-attachments/assets/2286704f-5c71-4384-8915-24909c8d3b1f) ![3D Transformation (Taichi) (18 92 FPS) 2026-03-23 23-00-48](https://github.com/user-attachments/assets/446cfb30-ec8a-4ea0-87ad-d4c7feffdb54)

### 3D 示例
1.**A 键**：绕 Y 轴顺时针旋转&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;      2.**D 键**：绕 Y 轴逆时针旋转

![3D Cube Transformation (Taichi) (59 95 FPS) 2026-03-25 18-07-17](https://github.com/user-attachments/assets/dfb91057-8107-4699-a7e1-5efd702d3114) ![3D Cube Transformation (Taichi) (59 95 FPS) 2026-03-25 18-07-17 (1)](https://github.com/user-attachments/assets/59af6213-76be-4a47-a219-44ab5a09679c)

3.**W 键**：绕 X 轴顺时针旋转&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; 4.**S 键**：绕 X 轴逆时针旋转

![3D Cube Transformation (Taichi) (59 95 FPS) 2026-03-25 18-07-17 (2)](https://github.com/user-attachments/assets/e0787bb0-cb9f-4be1-9fda-0d53aa58223a) ![3D Cube Transformation (Taichi) (59 95 FPS) 2026-03-25 18-07-17 (3)](https://github.com/user-attachments/assets/4a815926-2a7b-4701-a294-3e7cf563f00a) 

5.**Q 键**：绕 Z 轴顺时针旋转&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; 6.**E 键**：绕 Z 轴逆时针旋转

![3D Cube Transformation (Taichi) (59 95 FPS) 2026-03-25 18-07-17 (4)](https://github.com/user-attachments/assets/7d732c3d-687c-4bca-a0da-5036ab08d43b) ![3D Cube Transformation (Taichi) (59 95 FPS) 2026-03-25 18-07-17 (6)](https://github.com/user-attachments/assets/d9e6127e-72d5-4f82-83e9-6cc66e374a67)


## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。
