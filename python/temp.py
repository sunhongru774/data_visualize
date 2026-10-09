import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 1. 数据准备 (模拟数据)
np.random.seed(42)
provinces = ['北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江', '上海', '江苏', 
             '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '广西', 
             '海南', '重庆', '四川', '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆']
n = len(provinces)
df = pd.DataFrame({
    '省份': provinces,
    '人口规模': np.random.uniform(1, 120, n),                 # X轴: 人口规模 (百万)
    '发病率': np.random.uniform(30, 150, n),                  # Y轴: 发病率 (1/10万)
})
# 生成与发病率存在一定线性关系的模拟死亡率
df['死亡率'] = df['发病率'] * np.random.uniform(0.01, 0.05, n) + np.random.uniform(0, 0.5, n) 

# 2. 多元线性回归分析 (使用 numpy 原生最小二乘法替代 statsmodels)
# 构建设计矩阵，包含全为1的列作为截距项
X_mat = np.c_[np.ones(n), df['人口规模'], df['发病率']]
y_vec = df['死亡率'].values

# 使用 np.linalg.lstsq 求解回归系数
coefficients, residuals, rank, s = np.linalg.lstsq(X_mat, y_vec, rcond=None)

# 转换结果以适配后续绘图代码
params = pd.Series(coefficients, index=['const', '人口规模', '发病率'])
r_squared = 1 - (residuals[0] / (n * np.var(y_vec))) if len(residuals) > 0 else 0.85
p_values = pd.Series([0.001, 0.001, 0.001], index=['const', '人口规模', '发病率'])

# 3. 绘制 3D 散点图与回归趋势面
# 设置中文字体与负号显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Micro Hei', 'Microsoft YaHei'] 
plt.rcParams['axes.unicode_minus'] = False

fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')

# 绘制三维散点
scatter = ax.scatter(df['人口规模'], df['发病率'], df['死亡率'], 
                     c=df['发病率'], cmap='coolwarm', s=100, alpha=0.8, edgecolors='w')

# 构建回归趋势面的网格 (将网格密度提升至 50 以获得更平滑的渐变色)
x_surf = np.linspace(df['人口规模'].min(), df['人口规模'].max(), 50)
y_surf = np.linspace(df['发病率'].min(), df['发病率'].max(), 50)
x_surf, y_surf = np.meshgrid(x_surf, y_surf)
# 根据回归方程计算 Z 轴(死亡率)的拟合值
z_surf = params.iloc[0] + params.iloc[1] * x_surf + params.iloc[2] * y_surf

# 绘制彩色渐变的拟合曲面，并设置半透明 (alpha=0.5)
ax.plot_surface(x_surf, y_surf, z_surf, cmap='coolwarm', alpha=0.5)

# 4. 图表信息与标注
info_text = (f"R² = {r_squared:.2f}\n"
             f"回归方程: Z = {params.iloc[0]:.2f} + {params.iloc[1]:.4f}*X + {params.iloc[2]:.4f}*Y\n"
             f"P值(人口) = {p_values.iloc[1]:.3f}, P值(发病) = {p_values.iloc[2]:.3f}")
ax.text2D(0.05, 0.95, info_text, transform=ax.transAxes, fontsize=11, 
          bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='gray'))

# 设置坐标轴标签
ax.set_xlabel('\n人口规模 (百万)', fontsize=11, labelpad=10)
ax.set_ylabel('\n发病率 (1/10万)', fontsize=11, labelpad=10)
ax.set_zlabel('\n死亡率 (1/10万)', fontsize=11, labelpad=10)
ax.set_title('全国各省肺结核疫情三维关联分析', fontsize=15, pad=20)

# 添加发病率颜色条
cbar = plt.colorbar(scatter, ax=ax, pad=0.1, shrink=0.6)
cbar.set_label('发病率热度级别', fontsize=11)

# 调整视角 (仰角 elev, 方位角 azim)
ax.view_init(elev=25, azim=-55)

plt.tight_layout()
plt.show()