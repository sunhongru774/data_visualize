# -*- coding: utf-8 -*-
"""
生成 Vue 直接嵌入的 SVG 图表（一键生成 2010~2020 全部年份）。
"""
from pathlib import Path
import json
import argparse

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT  = ROOT / "public" / "charts"
OUT.mkdir(parents=True, exist_ok=True)

YEAR_START = 2010
YEAR_END   = 2020

for family in ["Noto Sans CJK SC", "Noto Sans CJK JP",
               "Microsoft YaHei", "SimHei"]:
    if any(family.lower() in f.name.lower()
           for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = family
        break

plt.rcParams.update({
    "axes.unicode_minus": False,
    "svg.fonttype": "none",
    "text.color": "white",
    "axes.labelcolor": "white",
    "axes.edgecolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "legend.labelcolor": "white",
    "legend.edgecolor": "white",
    "figure.facecolor": "none",
    "savefig.facecolor": "none",
})

BG = "none"
TEXT = "#ffffff"
GRID = "#2f5a73"
ACCENT = "#31d6ff"


def grad_colors(n, c1, c2):
    cmap = LinearSegmentedColormap.from_list("g", [c1, c2])
    return [cmap(i / max(n - 1, 1)) for i in range(n)]


def save(fig, name, year=None):
    if year is not None:
        name = name.replace(".svg", f"_{year}.svg")
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


# ---------------- 职业分布 ----------------
def career_chart():
    labels = ['农牧渔民', '家务及待业', '工人', '学生', '离退休人员']
    proportions = [61.50, 9.32, 5.89, 5.44, 4.69]
    cases = [13421197, 2033078, 1285335, 1186104, 1022406]

    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    width = (2 * np.pi / n) * 0.85
    colors = ['#a5e3d8', '#7dd3fc', '#c4b5fd', '#fcd34d', '#fca5a5']
    heights = [c / max(cases) for c in cases]

    fig = plt.figure(figsize=(6.5, 5.5), dpi=160)
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    inner = 0.35
    bars = ax.bar(angles, heights, width=width, bottom=inner,
                  color=colors, edgecolor='#061824', linewidth=1.2)
    ax.set_ylim(0, inner + 1.20)
    ax.set_yticks([])
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=11, color=TEXT)
    ax.tick_params(axis='x', pad=18)
    ax.grid(color=GRID, alpha=0.4, linewidth=0.7)
    ax.spines['polar'].set_color(GRID)
    ax.spines['polar'].set_alpha(0.4)

    for ang, bar, pct in zip(angles, bars, proportions):
        r = bar.get_y() + bar.get_height() + 0.08
        ax.text(ang, r, f'{pct:.2f}%', ha='center', va='center',
                color=TEXT, fontsize=9.5, fontweight='bold')

    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    save(fig, 'career.svg')


# ---------------- 十年趋势 ----------------
def trend_chart(year=2020):
    years = [2010, 2011, 2012, 2013, 2014, 2015,
             2016, 2017, 2018, 2019, 2020]
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

    if year in years:
        idx = years.index(year)
        ax.scatter([years[idx]], [cases[idx]], s=180,
                   facecolors='none', edgecolors='#facc15',
                   linewidths=2.5, zorder=8)
        ax.annotate(f"{year}\n{cases[idx]:,}",
                    (years[idx], cases[idx]),
                    textcoords="offset points", xytext=(0, 16),
                    ha="center", color="#facc15", fontsize=9, zorder=9)

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
    save(fig, "trend.svg", year)


# ---------------- 年龄组（从 age_by_year.json 读） ----------------
def age_chart(year=2020):
    p = ROOT / "public" / "data" / "age_by_year.json"
    if not p.exists():
        print(f"  [年龄] 缺少 {p.name}，跳过")
        return
    age_data = json.loads(p.read_text(encoding="utf-8"))
    d = age_data.get(str(year))
    if not d:
        print(f"  [年龄] {year} 年没有数据，跳过")
        return

    age_groups = d["age_groups"]
    cases      = d["cases"]
    incidence  = d["incidence"]

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
    line_cmap = LinearSegmentedColormap.from_list(
        "l", ["#31d6ff", "#facc15"])
    ax2.plot(x, incidence, color="#facc15", linewidth=2.2, zorder=5)
    ax2.scatter(x, incidence, c=incidence, cmap=line_cmap, s=30,
                zorder=6, edgecolors="#061824", linewidths=0.7)
    ax2.set_ylabel("发病率（1/10万）", fontsize=10, color=TEXT)
    ax2.tick_params(axis="y", colors=TEXT, labelsize=8)
    for sp in ax2.spines.values():
        sp.set_visible(False)

    fig.patch.set_alpha(0)
    save(fig, "age_bar.svg", year)


# ---------------- 各省 TOP10 ----------------
def province_top10(year=2020):
    p = ROOT / "public" / "data" / "zone_data_by_year.json"
    if not p.exists():
        print(f"  [TOP10] 缺少 {p.name}，跳过")
        return
    by_year = json.loads(p.read_text(encoding="utf-8"))
    ydata = by_year.get(str(year), {})
    if not ydata:
        print(f"  [TOP10] {year} 年数据为空，跳过")
        return
    rows = [{"name": k, "incidence": v.get("incidence", 0)}
            for k, v in ydata.items()]
    df = (pd.DataFrame(rows)
          .sort_values("incidence", ascending=False)
          .head(10)
          .sort_values("incidence"))

    fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=160)
    ax.set_facecolor(BG)
    fig.subplots_adjust(left=0.22, right=0.96, top=0.94, bottom=0.14)
    bar_colors = grad_colors(len(df), "#0ea5e9", "#ef4444")
    bars = ax.barh(df["name"], df["incidence"],
                   color=bar_colors, alpha=.9, height=.62)
    style_ax(ax)
    ax.grid(axis="x", color=GRID, alpha=.35, linewidth=.6)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel(f"{year} 年发病率（1/10万）", fontsize=10, color=TEXT)
    ax.tick_params(axis="y", labelsize=9, colors=TEXT)
    ax.tick_params(axis="x", labelsize=8, colors=TEXT)
    x_max = max(df["incidence"]) if len(df) else 1
    for b, v in zip(bars, df["incidence"]):
        ax.text(v + x_max * 0.015,
                b.get_y() + b.get_height() / 2,
                f"{v:.1f}", va="center", color=TEXT, fontsize=8)
    save(fig, "province_top10.svg", year)


# ---------------- 散点 ----------------
def scatter_correlation(year=2020):
    p = ROOT / "public" / "data" / "zone_data_by_year.json"
    if not p.exists():
        print(f"  [散点] 缺少 {p.name}，跳过")
        return
    by_year = json.loads(p.read_text(encoding="utf-8"))
    ydata = by_year.get(str(year), {})
    if not ydata:
        print(f"  [散点] {year} 年数据为空，跳过")
        return
    rows = [{"name": k,
             "incidence": v.get("incidence", 0),
             "mortality": v.get("mortality", 0)}
            for k, v in ydata.items()]
    df = pd.DataFrame(rows).dropna(subset=["incidence", "mortality"])
    if len(df) < 3:
        print(f"  [散点] {year} 年有效省份 < 3，跳过")
        return
    x = df["incidence"].to_numpy(dtype=float)
    y = df["mortality"].to_numpy(dtype=float)
    n = len(x)
    slope, intercept, r_value, p_value, _ = stats.linregress(x, y)
    r_squared = r_value ** 2
    x_fit = np.linspace(x.min(), x.max(), 100)
    y_fit = slope * x_fit + intercept
    y_pred = slope * x + intercept
    residuals = y - y_pred
    s_err = np.sqrt(np.sum(residuals ** 2) / (n - 2))
    t_val = stats.t.ppf(0.975, n - 2)
    se_fit = s_err * np.sqrt(
        1 / n + (x_fit - x.mean()) ** 2 / np.sum((x - x.mean()) ** 2))
    ci_upper = y_fit + t_val * se_fit
    ci_lower = y_fit - t_val * se_fit

    if p_value < 0.001:   stars = "***"
    elif p_value < 0.01:  stars = "**"
    elif p_value < 0.05:  stars = "*"
    else:                 stars = "n.s."

    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=160)
    ax.set_facecolor(BG)
    fig.subplots_adjust(left=0.12, right=0.90, top=0.94, bottom=0.15)
    cmap = LinearSegmentedColormap.from_list(
        "sc", ["#31d6ff", "#facc15", "#ef4444"])
    sc = ax.scatter(x, y, c=y, cmap=cmap, s=60, alpha=0.9,
                    edgecolors="#061824", linewidths=1.0, zorder=5)
    ax.plot(x_fit, y_fit, color="#facc15", linewidth=2.2, zorder=4)
    ax.fill_between(x_fit, ci_lower, ci_upper,
                    color="#facc15", alpha=0.15, zorder=3)

    sign = "+" if intercept >= 0 else "-"
    eq_text = (f"{year} 年\n"
               f"y = {slope:.4f}x {sign} {abs(intercept):.4f}\n"
               f"R = {r_value:.3f}   R² = {r_squared:.3f}\n"
               f"p = {p_value:.4e} {stars}   n = {n}")
    ax.text(0.04, 0.96, eq_text, transform=ax.transAxes,
            va="top", ha="left", color=TEXT, fontsize=9,
            bbox=dict(boxstyle="round,pad=0.4",
                      facecolor="#0b2a42",
                      edgecolor="#31d6ff", alpha=0.9))
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
    save(fig, "age_scatter.svg", year)


# ---------------- 入口 ----------------
def build_one_year(y, first_year):
    print(f"===== 年份 {y} =====")
    if y == first_year:
        career_chart()
        print("  career.svg")
    trend_chart(y);            print(f"  trend_{y}.svg")
    age_chart(y);              print(f"  age_bar_{y}.svg")
    province_top10(y);         print(f"  province_top10_{y}.svg")
    scatter_correlation(y);    print(f"  age_scatter_{y}.svg")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=None,
                        help="只生成指定年份；不传则生成全部")
    args = parser.parse_args()

    if args.year is not None:
        build_one_year(args.year, first_year=None)
    else:
        print(f"########## 一键生成 {YEAR_START}~{YEAR_END} 全部年份 ##########")
        for y in range(YEAR_START, YEAR_END + 1):
            build_one_year(y, first_year=YEAR_START)
        print(f"\n全部完成 -> {OUT}")


if __name__ == "__main__":
    main()