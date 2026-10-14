# -*- coding: utf-8 -*-
"""按年份生成 public/data/zone_<year>.json"""
import os, json, copy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PUB_DIR  = os.path.join(BASE_DIR, "public", "data")
os.makedirs(PUB_DIR, exist_ok=True)

NAME_MAP = {
    "北京市":"北京","天津市":"天津","上海市":"上海","重庆市":"重庆",
    "河北省":"河北","山西省":"山西","辽宁省":"辽宁","吉林省":"吉林",
    "黑龙江省":"黑龙江","江苏省":"江苏","浙江省":"浙江","安徽省":"安徽",
    "福建省":"福建","江西省":"江西","山东省":"山东","河南省":"河南",
    "湖北省":"湖北","湖南省":"湖南","广东省":"广东","海南省":"海南",
    "四川省":"四川","贵州省":"贵州","云南省":"云南","陕西省":"陕西",
    "甘肃省":"甘肃","青海省":"青海","台湾省":"台湾",
    "内蒙古自治区":"内蒙古","广西壮族自治区":"广西",
    "西藏自治区":"西藏","宁夏回族自治区":"宁夏",
    "新疆维吾尔自治区":"新疆",
    "香港特别行政区":"香港","澳门特别行政区":"澳门",
}
def norm(n): return NAME_MAP.get(str(n).strip(), str(n).strip())

def main():
    china = json.load(open(os.path.join(DATA_DIR,"china_base.json"), encoding="utf-8"))
    by_year = json.load(open(os.path.join(PUB_DIR,"zone_data_by_year.json"), encoding="utf-8"))

    for y, pmap in by_year.items():
        m = copy.deepcopy(china)
        for feat in m.get("features", []):
            props = feat.setdefault("properties", {})
            p = norm(props.get("name",""))
            info = pmap.get(p, {})
            props["value"]     = info.get("incidence", 0)
            props["incidence"] = info.get("incidence", 0)
            props["mortality"] = info.get("mortality", 0)
            props["cases"]     = info.get("cases", 0)
            props["deaths"]    = info.get("deaths", 0)
        out = os.path.join(PUB_DIR, f"zone_{y}.json")
        json.dump(m, open(out,"w",encoding="utf-8"), ensure_ascii=False)
        print("已生成:", out)

if __name__ == "__main__":
    main()