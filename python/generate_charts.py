# -*- coding: utf-8 -*-
"""使用用户提供的 Excel 数据生成 Vue 直接嵌入的 SVG 图表。"""
from pathlib import Path
import json
import math
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "public" / "charts"
OUT.mkdir(parents=True, exist_ok=True)

# 解决中文字体问题
for family in ["Noto Sans CJK SC", "Noto Sans CJK JP", "Microsoft YaHei", "SimHei"]:
    if any(family.lower() in f.name.lower() for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = family
        break
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["svg.fonttype"] = "none"

BG = "none"
TEXT = "#d9f7ff"
MUTED = "#7fb3c3"
GRID = "#285367"
ACCENT = "#31d6ff"
ACCENT2 = "#7ae7ff"
BAR = "#0aa6c8"


def save(fig, name):
    fig.savefig(OUT / name, format="svg", transparent=True, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def style_ax(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=TEXT, labelsize=8)
    ax.grid(axis="y", color=GRID, alpha=.35, linewidth=.6)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.xaxis.label.set_color(MUTED); ax.yaxis.label.set_color(MUTED)


def career_chart():
    df = pd.read_excel(DATA / "career.xls", sheet_name=0, header=0)
    df.columns = [str(x).strip() for x in df.columns]
    pct_col = df.columns[3]
    job_col = df.columns[1]
    df["构成比（%）"] = pd.to_numeric(df[pct_col], errors="coerce")
    df["职业"] = df[job_col].astype(str)
    df = df.dropna(subset=["构成比（%）"])
    vals = df["构成比（%）"].to_numpy()
    labels = df["职业"].tolist()
    fig, ax = plt.subplots(figsize=(5.9, 3.25), dpi=160)
    wedges, _ = ax.pie(vals, startangle=90, counterclock=False,
                       wedgeprops={"width": .36, "edgecolor": "#061824", "linewidth": 1.0},
                       colors=["#14b8a6", "#38bdf8", "#818cf8", "#f59e0b", "#ef4444"][:len(vals)])
    top = df.iloc[vals.argmax()]
    ax.text(0, .07, top["职业"], ha="center", va="center", color=TEXT, fontsize=13, weight="bold")
    ax.text(0, -.13, f"{top['构成比（%）']:.2f}%", ha="center", va="center", color=ACCENT, fontsize=14, weight="bold")
    ax.legend(wedges, [f"{n}  {v:.2f}%" for n,v in zip(labels, vals)],
              loc="center left", bbox_to_anchor=(.94,.5), frameon=False,
              labelcolor=TEXT, fontsize=8, handlelength=.8)
    ax.set_aspect("equal"); fig.patch.set_alpha(0); save(fig, "career.svg")
    return {"name": str(top["职业"]), "rate": float(top["构成比（%）"])}


def trend_chart():
    raw = pd.read_excel(DATA / "ten_years.xlsx", header=None)
    years, cases = [], []
    for c in range(1, raw.shape[1], 4):
        y = raw.iat[1,c]
        if pd.notna(y):
            try:
                y = int(y); years.append(y); cases.append(float(raw.iat[3,c]))
            except Exception: pass
    order = sorted(zip(years,cases))
    years, cases = zip(*order)
    fig, ax = plt.subplots(figsize=(7.0, 3.15), dpi=160)
    ax.plot(years, cases, color=ACCENT, marker="o", markersize=3.7, linewidth=2.2)
    ax.fill_between(years, cases, [min(cases)]*len(cases), color="#0ea5e9", alpha=.10)
    style_ax(ax); ax.set_xlabel("年份", fontsize=8); ax.set_ylabel("发病数（例）", fontsize=8)
    ax.set_xticks(years); ax.tick_params(axis="x", rotation=0, labelsize=7)
    for x,y in zip(years,cases):
        if x in (min(years), max(years)):
            ax.annotate(f"{y:,.0f}", (x,y), textcoords="offset points", xytext=(0,8), ha="center", color=ACCENT2, fontsize=7)
    save(fig, "trend.svg")


def age_chart():
    # 数据来源：ReportAgeYear.xls 中“肺结核”列（0-89岁各年龄组）
    # 注意：原文件把发病数错误显示为 1900-01-XX 日期，这里已用 Excel 序列号规则还原
    age_groups = ['0-','1-','2-','3-','4-','5-','6-','7-','8-','9-',
                  '10-','15-','20-','25-','30-','35-','40-','45-',
                  '50-','55-','60-','65-','70-','75-','80-','85及以上']
    cases = [162, 125, 98, 120, 136, 135, 197, 207, 239, 279,
             6359, 38870, 52298, 50466, 48296, 34815, 36222, 51025,
             61989, 59266, 55637, 61608, 48048, 33514, 20157, 10229]
    incidence = [1.0783, 0.8151, 0.5836, 0.7158, 0.8123, 0.8950, 1.2104, 1.3081,
                 1.5464, 1.8125, 8.2669, 54.2137, 66.1050, 47.9777, 39.9653,
                 34.8450, 36.5648, 41.5033, 51.7880, 62.2609, 71.2930, 87.0038,
                 104.7987, 115.3133, 109.4935, 82.8900]

    x = list(range(len(age_groups)))
    fig, ax1 = plt.subplots(figsize=(7.15, 3.35), dpi=160)
    ax1.bar(x, cases, width=.64, color=BAR, alpha=.72)
    ax1.set_ylabel("发病数（例）", color=MUTED, fontsize=8)
    ax1.tick_params(axis="y", colors=TEXT, labelsize=7)
    ax1.set_xticks(x)
    ax1.set_xticklabels(age_groups, color=TEXT, fontsize=7, rotation=45, ha="right")
    ax1.grid(axis="y", color=GRID, alpha=.28, linewidth=.6)
    for sp in ax1.spines.values(): sp.set_visible(False)

    ax2 = ax1.twinx()
    ax2.plot(x, incidence, color="#facc15", marker="o", markersize=3.1, linewidth=2.0)
    ax2.set_ylabel("发病率（1/10万）", color=MUTED, fontsize=8)
    ax2.tick_params(axis="y", colors=TEXT, labelsize=7)
    for sp in ax2.spines.values(): sp.set_visible(False)

    ax1.set_facecolor(BG); fig.patch.set_alpha(0)
    save(fig, "age_bar.svg")


def province_top10():
    data = json.loads((ROOT / "public" / "data" / "zone_data.json").read_text(encoding="utf-8"))
    df = pd.DataFrame(data).sort_values("incidence", ascending=False).head(10).sort_values("incidence")
    fig, ax = plt.subplots(figsize=(7.0, 3.3), dpi=160)
    bars = ax.barh(df["name"], df["incidence"], color=ACCENT, alpha=.78, height=.62)
    style_ax(ax); ax.set_xlabel("发病率（1/10万）", fontsize=8)
    ax.tick_params(axis="y", labelsize=7)
    for b,v in zip(bars,df["incidence"]):
        ax.text(v + max(df["incidence"])*.01, b.get_y()+b.get_height()/2, f"{v:.1f}", va="center", color=TEXT, fontsize=7)
    save(fig, "province_top10.svg")


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
    update_summary(top)
    print("SVG 图表生成完成：", OUT)
