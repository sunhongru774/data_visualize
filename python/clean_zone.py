# -*- coding: utf-8 -*-
"""清洗省级肺结核数据。
当前用户提供的数据中没有 ReportZoneYear.xls，而 ten_years.xlsx 已包含 2010-2020 年
全国及各省的发病数、死亡数、发病率和死亡率，因此本脚本以 ten_years.xlsx 作为省级数据源。
"""
from pathlib import Path
import json
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "ten_years.xlsx"
OUT = ROOT / "public" / "data" / "zone_data.json"
SUMMARY = ROOT / "public" / "data" / "dashboard_summary.json"

PROVINCE_ALIASES = {
    "内蒙古": "内蒙古自治区", "广西": "广西壮族自治区", "西藏": "西藏自治区",
    "宁夏": "宁夏回族自治区", "新疆": "新疆维吾尔自治区", "北京": "北京市",
    "天津": "天津市", "上海": "上海市", "重庆": "重庆市",
    "河北": "河北省", "山西": "山西省", "辽宁": "辽宁省", "吉林": "吉林省",
    "黑龙江": "黑龙江省", "江苏": "江苏省", "浙江": "浙江省", "安徽": "安徽省",
    "福建": "福建省", "江西": "江西省", "山东": "山东省", "河南": "河南省",
    "湖北": "湖北省", "湖南": "湖南省", "广东": "广东省", "海南": "海南省",
    "四川": "四川省", "贵州": "贵州省", "云南": "云南省", "陕西": "陕西省",
    "甘肃": "甘肃省", "青海": "青海省", "台湾": "台湾省"
}

def clean_name(x):
    s = re.sub(r"\s+", "", str(x)).strip()
    if s in {"全国", "全"}: return "全国"
    return PROVINCE_ALIASES.get(s, s)

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"找不到 {INPUT}")
    raw = pd.read_excel(INPUT, header=None)
    years = []
    for c in range(1, raw.shape[1], 4):
        v = raw.iat[1, c]
        if pd.notna(v):
            years.append((int(v), c))
    # 只保留有完整四列指标的年份
    years = [(y, c) for y, c in years if c + 3 < raw.shape[1]]
    if not years:
        raise ValueError("ten_years.xlsx 未识别出年份列")
    target_year = 2020 if any(y == 2020 for y, _ in years) else max(y for y, _ in years)
    col = dict(years)[target_year]
    records = []
    for r in range(3, raw.shape[0]):
        name = clean_name(raw.iat[r, 0])
        if not name or name == "全国":
            continue
        vals = [raw.iat[r, col+i] for i in range(4)]
        if all(pd.isna(v) for v in vals):
            continue
        cases = float(vals[0]) if pd.notna(vals[0]) else 0
        deaths = float(vals[1]) if pd.notna(vals[1]) else 0
        incidence = float(vals[2]) if pd.notna(vals[2]) else 0
        mortality = float(vals[3]) if pd.notna(vals[3]) else 0
        records.append({"name": name, "cases": cases, "deaths": deaths,
                        "incidence": incidence, "mortality": mortality, "year": target_year})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    nat = raw[raw[0].astype(str).str.replace(" ", "", regex=False).isin(["全国", "全"])].iloc[0]
    nidx = col
    national = {
        "cases": float(nat.iloc[nidx]),
        "deaths": float(nat.iloc[nidx+1]),
        "incidence": float(nat.iloc[nidx+2]),
        "mortality": float(nat.iloc[nidx+3])
    }
    summary = {"metrics": national, "year": target_year}
    # careerTop 在 generate_charts.py 中补充
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成：{OUT}")
    print(f"目标年份：{target_year}；省级记录：{len(records)}")

if __name__ == "__main__":
    main()
