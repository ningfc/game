import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from itertools import combinations

# 示例点集
old_points = np.array([[1, 1], [3, 1], [2, 3], [4, 2]])  # 旧点集 (红色)
new_points = np.array([[2, 2], [4, 2], [3, 4], [5, 3], [6, 1]])  # 新点集 (黑色)

# 使用更多的点模拟，并加入随机偏移，使点不能完全重合
np.random.seed(42)
# # 模拟旧点集：生成30个点，范围在[1, 7]之间
all_pionts = np.random.rand(10, 2) * 6 + 1
new_points = all_pionts
# # 对旧点集施加旋转、缩放和平移生成新点集
angle = np.deg2rad(0)  # 旋转角度30度
scale = 1            # 缩放因子
R = np.array([[np.cos(angle), -np.sin(angle)],
              [np.sin(angle),  np.cos(angle)]])
translation = np.array([1, -1])

idx = np.random.choice(all_pionts.shape[0], 3, replace=False)
old_points = all_pionts[idx]
old_points = (old_points @ R.T) * scale + translation

# # 添加高斯噪声，使新点与理论计算结果有细微偏差
# new_points += np.random.normal(0, 0.1, new_points.shape)

# 计算两点间距离
def distance(p1, p2):
    return np.linalg.norm(p1 - p2)

# 推算第三个点位置
def find_third_point(p1, p2, d13, d23, tol=0.2):
    v = p2 - p1
    d12 = distance(p1, p2)
    cos_theta = (d12**2 + d13**2 - d23**2) / (2 * d12 * d13)
    if abs(cos_theta) > 1:  # 避免数值误差
        return None, None
    sin_theta = np.sqrt(max(0, 1 - cos_theta**2))
    p3_1 = p1 + np.array([cos_theta * d13, sin_theta * d13])
    p3_2 = p1 + np.array([cos_theta * d13, -sin_theta * d13])
    return p3_1, p3_2

# 检查点是否存在
def check_point_exists(p, points, tol=0.2):
    return np.any(np.linalg.norm(points - p, axis=1) < tol)

# 计算变换并验证所有点
def compute_transform_and_verify(old_triangle, new_triangle, old_points, new_points, tol=0.2):
    old_center = np.mean(old_triangle, axis=0)
    new_center = np.mean(new_triangle, axis=0)
    old_shifted = old_triangle - old_center
    new_shifted = new_triangle - new_center
    H = old_shifted.T @ new_shifted
    U, _, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    scale = np.linalg.norm(new_shifted) / np.linalg.norm(old_shifted)
    transformed_points = (old_points - old_center) @ R * scale + new_center
    matches = sum(check_point_exists(tp, new_points, tol) for tp in transformed_points)
    return transformed_points if matches == len(old_points) else None

# 匹配算法（返回动画所需的关键步骤数据）
def match_points_with_steps(old_points, new_points, tol=0.2):
    steps = []
    for old_tri_idx in combinations(range(len(old_points)), 3):
        old_triangle = old_points[list(old_tri_idx)]
        d12 = distance(old_triangle[0], old_triangle[1])
        d13 = distance(old_triangle[0], old_triangle[2])
        d23 = distance(old_triangle[1], old_triangle[2])
        steps.append(("select_triangle", old_triangle))
        
        for i, j in combinations(range(len(new_points)), 2):
            p1, p2 = new_points[i], new_points[j]
            d = distance(p1, p2)
            if abs(d - d12) < tol:
                steps.append(("select_two_points", np.array([p1, p2])))
                p3_1, p3_2 = find_third_point(p1, p2, d13, d23, tol)
                if p3_1 is None:
                    continue
                steps.append(("predict_third", p3_1))
                if check_point_exists(p3_1, new_points, tol):
                    new_triangle = np.array([p1, p2, p3_1])
                    steps.append(("third_found", new_triangle))
                    result = compute_transform_and_verify(old_triangle, new_triangle, old_points, new_points, tol)
                    if result is not None:
                        steps.append(("verify_all", result))
                        return result, steps
                else:
                    steps.append(("predict_third", p3_2))
                    if check_point_exists(p3_2, new_points, tol):
                        new_triangle = np.array([p1, p2, p3_2])
                        steps.append(("third_found", new_triangle))
                        result = compute_transform_and_verify(old_triangle, new_triangle, old_points, new_points, tol)
                        if result is not None:
                            steps.append(("verify_all", result))
                            return result, steps
    return None, steps

# 执行匹配并获取步骤
transformed_points, steps = match_points_with_steps(old_points, new_points)

# 动画设置
fig, ax = plt.subplots()
ax.set_xlim(0, 7)
ax.set_ylim(0, 7)
ax.set_title("Point Set Matching Steps Animation")

new_scatter = ax.scatter(new_points[:, 0], new_points[:, 1], c='black', label='New Points')
old_scatter = ax.scatter(old_points[:, 0], old_points[:, 1], c='red', label='Old Points')
process_scatter = ax.scatter([], [], c='blue', marker='+', label='Process', s=100)
result_scatter = ax.scatter([], [], c='green', marker='x', label='Result', s=100)
ax.legend()

# 动画帧更新函数
def update(frame):
    process_scatter.set_offsets(np.empty((0, 2)))
    result_scatter.set_offsets(np.empty((0, 2)))
    
    if frame < len(steps):
        step_type, data = steps[frame]
        if step_type == "select_triangle":
            process_scatter.set_offsets(data)
        elif step_type == "select_two_points":
            process_scatter.set_offsets(data)
        elif step_type == "predict_third":
            process_scatter.set_offsets(np.array([data]))
        elif step_type == "third_found":
            process_scatter.set_offsets(data)
        elif step_type == "verify_all":
            result_scatter.set_offsets(data)
    elif transformed_points is not None:
        result_scatter.set_offsets(transformed_points)
    
    return new_scatter, old_scatter, process_scatter, result_scatter

# 创建动画
frame_count = len(steps) + 10  # 多加几帧显示最终结果
ani = FuncAnimation(fig, update, frames=frame_count, interval=500, blit=True)

# 显示动画
plt.show()

# 保存动画（可选）
# ani.save('point_matching_steps.gif', writer='pillow')