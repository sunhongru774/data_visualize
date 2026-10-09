# -*- coding: utf-8 -*-
"""生成 Vue 直接嵌入的 SVG 图表（全白色文字 + 渐变色 + 散点回归）。"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "public" / "charts"
OUT.mkdir(parents=True, exist_ok=True)

# ---------- 字体 ----------
for family in ["Noto Sans CJK SC", "Noto Sans CJK JP", "Microsoft YaHei", "SimHei"]:
    if any(family.lower() in f.name.lower() for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = family
        break

# ---------- 全局样式：所有文字白色 ----------
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["text.color"] = "white"
plt.rcParams["axes.labelcolor"] = "white"
plt.rcParams["axes.edgecolor"] = "white"
plt.rcParams["xtick.color"] = "white"
plt.rcParams["ytick.color"] = "white"
plt.rcParams["legend.labelcolor"] = "white"
plt.rcParams["legend.edgecolor"] = "white"
plt.rcParams["figure.facecolor"] = "none"
plt.rcParams["savefig.facecolor"] = "none"

BG = "none"
TEXT = "#ffffff"
GRID = "#2f5a73"
ACCENT = "#31d6ff"


def grad_colors(n, c1, c2):
    cmap = LinearSegmentedColormap.from_list("g", [c1, c2])
    return [cmap(i / max(n - 1, 1)) for i in range(n)]


def save(fig, name):
    fig.savefig(OUT / name, format="svg", transparent=True,
                bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def style_ax(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=TEXT, labelsize=8)
    ax.grid(axis="y", color=GRID, alpha=.35, linewidth=.6)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)


# ---------- 1. 职业分布：南丁格尔玫瑰图（参考你给的样图） ----------
def career_chart():
    labels = ['农牧渔民', '家务及待业', '工人', '学生', '离退休人员']
    proportions = [61.50, 9.32, 5.89, 5.44, 4.69]
    cases = [13421197, 2033078, 1285335, 1186104, 1022406]

    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    width = (2 * np.pi / n) * 0.85

    # 柔和配色（参考图同款色系）
    colors = ['#a5e3d8', '#7dd3fc', '#c4b5fd', '#fcd34d', '#fca5a5']

    max_case = max(cases)
    heights = [c / max_case * 1.0 for c in cases]

    fig = plt.figure(figsize=(6.5, 5.5), dpi=160)
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    inner = 0.35
    bars = ax.bar(angles, heights, width=width, bottom=inner,
                  color=colors, edgecolor='#061824', linewidth=1.2)

    ax.set_ylim(0, inner + 1.20)

    # 隐藏径向刻度线，只保留外圈角度标签
    ax.set_yticks([])
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=11, color=TEXT)
    ax.tick_params(axis='x', pad=18)

    # 极坐标网格
    ax.grid(color=GRID, alpha=0.4, linewidth=0.7)
    ax.spines['polar'].set_color(GRID)
    ax.spines['polar'].set_alpha(0.4)

    # 每个扇区上方标百分比
    for ang, bar, pct in zip(angles, bars, proportions):
        r = bar.get_y() + bar.get_height() + 0.08
        ax.text(ang, r, f'{pct:.2f}%', ha='center', va='center',
                color=TEXT, fontsize=9.5, fontweight='bold')

    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    save(fig, 'career.svg')

    top_idx = int(np.argmax(proportions))
    return {'name': labels[top_idx], 'rate': proportions[top_idx]}


# ---------- 2. 全国十年趋势 ----------
def trend_chart():
    years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
    cases = [991350, 953275, 951508, 904434, 889381, 864015,
             836236, 835193, 823342, 775764, 670538]

    fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=160)
    ax.set_facecolor(BG)

    cmap = LinearSegmentedColormap.from_list("t", ["#0ea5e9", "#7c3aed"])
    ymin = min(cases) * 0.92
    for i in range(len(years) - 1):
        ax.fill_between([years[i], years[i + 1]],
                        [cases[i], cases[i + 1]],
                        [ymin, ymin],
                        color=cmap(i / max(len(years) - 2, 1)),
                        alpha=0.35, linewidth=0)

    ax.plot(years, cases, color=ACCENT, linewidth=2.4, zorder=5)
    ax.scatter(years, cases, c=range(len(years)),
               cmap=cmap, s=55, zorder=6,
               edgecolors="#061824", linewidths=0.9)

    style_ax(ax)
    ax.set_xlabel("年份", fontsize=10, color=TEXT)
    ax.set_ylabel("发病数（例）", fontsize=10, color=TEXT)
    ax.set_xticks(years)
    ax.tick_params(axis="x", labelsize=8, colors=TEXT)
    ax.tick_params(axis="y", labelsize=8, colors=TEXT)
    ax.set_ylim(ymin, max(cases) * 1.05)

    for x, y in zip([years[0], years[-1]], [cases[0], cases[-1]]):
        ax.annotate(f"{y:,}", (x, y), textcoords="offset points",
                    xytext=(0, 10), ha="center", color=TEXT, fontsize=8)

    save(fig, "trend.svg")


# ---------- 3. 年龄组柱状图 + 发病率折线 ----------
def age_chart():
    age_groups = ['0-', '1-', '2-', '3-', '4-', '5-', '6-', '7-', '8-', '9-',
                  '10-', '15-', '20-', '25-', '30-', '35-', '40-', '45-',
                  '50-', '55-', '60-', '65-', '70-', '75-', '80-', '85+']
    cases = [162, 125, 98, 120, 136, 135, 197, 207, 239, 279,
             6359, 38870, 52298, 50466, 48296, 34815, 36222, 51025,
             61989, 59266, 55637, 61608, 48048, 33514, 20157, 10229]
    incidence = [1.0783, 0.8151, 0.5836, 0.7158, 0.8123, 0.8950, 1.2104, 1.3081,
                 1.5464, 1.8125, 8.2669, 54.2137, 66.1050, 47.9777, 39.9653,
                 34.8450, 36.5648, 41.5033, 51.7880, 62.2609, 71.2930, 87.0038,
                 104.7987, 115.3133, 109.4935, 82.8900]

    x = list(range(len(age_groups)))
    fig, ax1 = plt.subplots(figsize=(7.6, 3.8), dpi=160)
    ax1.set_facecolor(BG)
    fig.subplots_adjust(bottom=0.30, left=0.10, right=0.90, top=0.92)

    bar_colors = grad_colors(len(age_groups), "#0aa6c8", "#7c3aed")
    ax1.bar(x, cases, width=.62, color=bar_colors, alpha=.9)

    ax1.set_ylabel("发病数（例）", fontsize=10, color=TEXT)
    ax1.tick_params(axis="y", colors=TEXT, labelsize=8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(age_groups, color=TEXT, fontsize=8,
                        rotation=45, ha="right", rotation_mode="anchor")
    ax1.grid(axis="y", color=GRID, alpha=.3, linewidth=.6)
    for sp in ax1.spines.values():
        sp.set_visible(False)

    ax2 = ax1.twinx()
    line_cmap = LinearSegmentedColormap.from_list("l", ["#31d6ff", "#facc15"])
    ax2.plot(x, incidence, color="#facc15", linewidth=2.2, zorder=5)
    ax2.scatter(x, incidence, c=incidence, cmap=line_cmap, s=30, zorder=6,
                edgecolors="#061824", linewidths=0.7)
    ax2.set_ylabel("发病率（1/10万）", fontsize=10, color=TEXT)
    ax2.tick_params(axis="y", colors=TEXT, labelsize=8)
    for sp in ax2.spines.values():
        sp.set_visible(False)

    fig.patch.set_alpha(0)
    save(fig, "age_bar.svg")


# ---------- 4. 各省发病率 TOP10 ----------
def province_top10():
    data = json.loads((ROOT / "public" / "data" / "zone_data.json").read_text(encoding="utf-8"))
    df = pd.DataFrame(data).sort_values("incidence", ascending=False).head(10).sort_values("incidence")

    fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=160)
    ax.set_facecolor(BG)
    fig.subplots_adjust(left=0.22, right=0.96, top=0.94, bottom=0.14)

    bar_colors = grad_colors(len(df), "#0ea5e9", "#ef4444")
    bars = ax.barh(df["name"], df["incidence"], color=bar_colors, alpha=.9, height=.62)

    style_ax(ax)
    ax.grid(axis="x", color=GRID, alpha=.35, linewidth=.6)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("发病率（1/10万）", fontsize=10, color=TEXT)
    ax.tick_params(axis="y", labelsize=9, colors=TEXT)
    ax.tick_params(axis="x", labelsize=8, colors=TEXT)

    x_max = max(df["incidence"])
    for b, v in zip(bars, df["incidence"]):
        ax.text(v + x_max * 0.015,
                b.get_y() + b.get_height() / 2,
                f"{v:.1f}", va="center", color=TEXT, fontsize=8)
    save(fig, "province_top10.svg")


# ---------- 5. 发病率 vs 死亡率 散点 + 回归 + 置信区间 ----------
def scatter_correlation():
    data = json.loads((ROOT / "public" / "data" / "zone_data.json").read_text(encoding="utf-8"))
    df = pd.DataFrame(data).dropna(subset=["incidence", "mortality"])
    x = df["incidence"].to_numpy(dtype=float)
    y = df["mortality"].to_numpy(dtype=float)
    n = len(x)

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    r_squared = r_value ** 2

    x_fit = np.linspace(x.min(), x.max(), 100)
    y_fit = slope * x_fit + intercept
    y_pred = slope * x + intercept
    residuals = y - y_pred
    s_err = np.sqrt(np.sum(residuals ** 2) / (n - 2))
    t_val = stats.t.ppf(0.975, n - 2)
    se_fit = s_err * np.sqrt(1 / n + (x_fit - x.mean()) ** 2 / np.sum((x - x.mean()) ** 2))
    ci_upper = y_fit + t_val * se_fit
    ci_lower = y_fit - t_val * se_fit

    if p_value < 0.001:
        stars = "***"
    elif p_value < 0.01:
        stars = "**"
    elif p_value < 0.05:
        stars = "*"
    else:
        stars = "n.s."

    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=160)
    ax.set_facecolor(BG)
    fig.subplots_adjust(left=0.12, right=0.90, top=0.94, bottom=0.15)

    cmap = LinearSegmentedColormap.from_list("sc", ["#31d6ff", "#facc15", "#ef4444"])
    sc = ax.scatter(x, y, c=y, cmap=cmap, s=60, alpha=0.9,
                    edgecolors="#061824", linewidths=1.0, zorder=5)

    ax.plot(x_fit, y_fit, color="#facc15", linewidth=2.2, zorder=4)
    ax.fill_between(x_fit, ci_lower, ci_upper, color="#facc15", alpha=0.15, zorder=3)

    sign = "+" if intercept >= 0 else "-"
    eq_text = (
        f"y = {slope:.4f}x {sign} {abs(intercept):.4f}\n"
        f"R = {r_value:.3f}   R² = {r_squared:.3f}\n"
        f"p = {p_value:.4e} {stars}   n = {n}"
    )
    ax.text(0.04, 0.96, eq_text, transform=ax.transAxes,
            va="top", ha="left", color=TEXT, fontsize=9,
            bbox=dict(boxstyle="round,pad=0.4",
                      facecolor="#0b2a42", edgecolor="#31d6ff", alpha=0.9))

    ax.set_xlabel("发病率（1/10万）", color=TEXT, fontsize=10)
    ax.set_ylabel("死亡率（1/10万）", color=TEXT, fontsize=10)
    ax.tick_params(colors=TEXT, labelsize=8)
    ax.grid(color=GRID, alpha=.3, linewidth=.6)
    for sp in ax.spines.values():
        sp.set_visible(False)

    cbar = fig.colorbar(sc, ax=ax, pad=0.015, fraction=0.045)
    cbar.set_label("死亡率", color=TEXT, fontsize=8)
    cbar.ax.tick_params(colors=TEXT, labelsize=7)
    cbar.outline.set_edgecolor(GRID)

    fig.patch.set_alpha(0)
    save(fig, "age_scatter.svg")

# 全国各省人口规模（第七次全国人口普查，单位：百万人），key 用省级全称
POPULATION_MILLION = {
    "北京市": 21.516, "天津市": 15.168, "河北省": 73.8375,
    "山西省": 36.4796, "内蒙古自治区": 25.0481, "辽宁省": 43.9100,
    "吉林省": 27.5238, "黑龙江省": 38.3300, "上海市": 24.2568,
    "江苏省": 79.6006, "浙江省": 55.0800, "安徽省": 60.8290,
    "福建省": 38.0600, "江西省": 45.4216, "山东省": 97.8943,
    "河南省": 94.3600, "湖北省": 58.1600, "湖南省": 67.3724,
    "广东省": 107.2400, "广西壮族自治区": 47.5400, "海南省": 9.0348,
    "重庆市": 29.9140, "四川省": 81.4020, "贵州省": 35.0803,
    "云南省": 47.1390, "西藏自治区": 3.1755, "陕西省": 37.7512,
    "甘肃省": 25.9078, "青海省": 5.8342, "宁夏回族自治区": 6.6154,
    "新疆维吾尔自治区": 22.9847,
}


# ---------- 8. 三维关联分析（人口规模 × 发病率 × 死亡率 + 回归趋势面） ----------
def scatter_3d_regional():
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    data = json.loads(
        (ROOT / "public" / "data" / "zone_data.json").read_text(encoding="utf-8")
    )
    df = pd.DataFrame(data).dropna(subset=["cases", "incidence", "mortality"]).copy()
    if df.empty:
        print("三维关联分析：zone_data.json 为空，跳过。")
        return

    # 按省级全称关联人口
    df["population"] = df["name"].map(POPULATION_MILLION)
    df = df.dropna(subset=["population"])

    print(f"三维关联分析：匹配到 {len(df)} 个省份的人口数据")

    if df.empty:
        print("三维关联分析：无匹配省份人口，跳过。")
        return

    X = df["population"].to_numpy(dtype=float)
    Y = df["incidence"].to_numpy(dtype=float)
    Z = df["mortality"].to_numpy(dtype=float)
    n = len(df)

    # 多元线性回归 Z = a + b·X + c·Y
    X_mat = np.c_[np.ones(n), X, Y]
    coefficients, residuals, rank, s = np.linalg.lstsq(X_mat, Z, rcond=None)
    a, b, c = coefficients[0], coefficients[1], coefficients[2]

    z_pred = X_mat @ coefficients
    ss_res = float(np.sum((Z - z_pred) ** 2))
    ss_tot = float(np.sum((Z - Z.mean()) ** 2))
    r_squared = 1 - ss_res / ss_tot if ss_tot > 1e-12 else 0.0

    df_model, df_resid = 2, n - 3
    p_value = 0.0
    if df_resid > 0 and 0 <= r_squared < 1:
        f_stat = (r_squared / df_model) / ((1 - r_squared) / df_resid)
        p_value = 1 - stats.f.cdf(f_stat, df_model, df_resid)

    cmap = LinearSegmentedColormap.from_list(
        "sc3d", ["#31d6ff", "#facc15", "#ef4444"]
    )

    fig = plt.figure(figsize=(7.6, 5.4), dpi=160)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor("none")

    scatter = ax.scatter(
        X, Y, Z,
        c=Y, cmap=cmap, s=62, alpha=0.88,
        edgecolors="white", linewidths=0.5, depthshade=False
    )

    x_grid = np.linspace(X.min(), X.max(), 30)
    y_grid = np.linspace(Y.min(), Y.max(), 30)
    xg, yg = np.meshgrid(x_grid, y_grid)
    zg = a + b * xg + c * yg
    ax.plot_surface(xg, yg, zg, cmap=cmap, alpha=0.32,
                    edgecolor="none", antialiased=True)

    info = (
        f"R² = {r_squared:.3f}\n"
        f"Z = {a:.3f} + {b:.5f}·X + {c:.5f}·Y\n"
        f"p = {p_value:.3e}    n = {n}"
    )
    ax.text2D(0.02, 0.98, info, transform=ax.transAxes,
              va="top", ha="left", color="#ffffff", fontsize=8,
              bbox=dict(boxstyle="round,pad=0.4",
                        facecolor="#0b2a42",
                        edgecolor="#31d6ff", alpha=0.92))

    ax.set_xlabel("人口规模（百万）", color="#ffffff", fontsize=8, labelpad=6)
    ax.set_ylabel("发病率（1/10万）", color="#ffffff", fontsize=8, labelpad=6)
    ax.set_zlabel("死亡率（1/10万）", color="#ffffff", fontsize=8, labelpad=6)

    ax.tick_params(colors="#ffffff", labelsize=6, pad=0)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.fill = False
        axis.pane.set_edgecolor("#2f5a73")
        axis.line.set_color("#2f5a73")
        axis._axinfo["grid"]["color"] = (0.18, 0.35, 0.45, 0.55)

    ax.view_init(elev=18, azim=-55)
    ax.set_box_aspect((1.15, 1.0, 0.8))

    cbar = fig.colorbar(scatter, ax=ax, pad=0.08, shrink=0.55)
    cbar.set_label("发病率", color="#ffffff", fontsize=7)
    cbar.ax.tick_params(colors="#ffffff", labelsize=6)
    cbar.outline.set_edgecolor("#2f5a73")

    fig.patch.set_alpha(0)
    save(fig, "scatter_3d.svg")

def update_summary(career_top):
    p = ROOT / "public" / "data" / "dashboard_summary.json"
    summary = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    summary["careerTop"] = career_top
    p.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    top = career_chart()
    trend_chart()
    age_chart()
    province_top10()
    scatter_correlation()
    scatter_3d_regional() 
    update_summary(top)
    print("SVG 图表生成完成：", OUT)