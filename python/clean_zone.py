# -*- coding: utf-8 -*-

"""
生成 ECharts 中国地图数据

输入：
data/ReportZoneYear.xls
data/china_base.json

输出：
src/data/zone.json
"""

import os
import re
import json
import xml.etree.ElementTree as ET

import pandas as pd
import numpy as np


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "src",
    "data"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# =====================================================
# 数值
# =====================================================

def to_number(value):

    if value is None:

        return 0

    if pd.isna(value):

        return 0

    text = str(value).strip()

    if not text:

        return 0

    text = (
        text
        .replace(",", "")
        .replace(" ", "")
        .replace("%", "")
    )

    try:

        return float(text)

    except Exception:

        return 0


# =====================================================
# XML XLS
# =====================================================

def read_xml_xls(
    file_path
):

    NS = {
        "ss":
        "urn:schemas-microsoft-com:office:spreadsheet"
    }

    root = ET.parse(
        file_path
    ).getroot()

    worksheet = root.find(
        ".//ss:Worksheet",
        NS
    )

    table = worksheet.find(
        "ss:Table",
        NS
    )

    rows = []

    for row in table.findall(
        "ss:Row",
        NS
    ):

        values = []

        for cell in row.findall(
            "ss:Cell",
            NS
        ):

            index = cell.attrib.get(
                "{%s}Index" %
                NS["ss"]
            )

            if index:

                target = (
                    int(index) - 1
                )

                while len(values) < target:

                    values.append(
                        None
                    )

            data = cell.find(
                "ss:Data",
                NS
            )

            if data is not None:

                values.append(
                    data.text
                )

            else:

                values.append(
                    None
                )

        rows.append(
            values
        )

    return pd.DataFrame(
        rows
    )


# =====================================================
# Excel
# =====================================================

def read_zone_excel():

    path = os.path.join(
        DATA_DIR,
        "ReportZoneYear.xls"
    )

    try:

        df = pd.read_excel(
            path
        )

    except Exception:

        df = read_xml_xls(
            path
        )

    return df


# =====================================================
# 省份名称标准化
# =====================================================

def normalize_name(
    name
):

    name = str(
        name
    ).strip()

    replace = {

        "北京市":
            "北京",

        "天津市":
            "天津",

        "上海市":
            "上海",

        "重庆市":
            "重庆",

        "河北省":
            "河北",

        "山西省":
            "山西",

        "辽宁省":
            "辽宁",

        "吉林省":
            "吉林",

        "黑龙江省":
            "黑龙江",

        "江苏省":
            "江苏",

        "浙江省":
            "浙江",

        "安徽省":
            "安徽",

        "福建省":
            "福建",

        "江西省":
            "江西",

        "山东省":
            "山东",

        "河南省":
            "河南",

        "湖北省":
            "湖北",

        "湖南省":
            "湖南",

        "广东省":
            "广东",

        "海南省":
            "海南",

        "四川省":
            "四川",

        "贵州省":
            "贵州",

        "云南省":
            "云南",

        "陕西省":
            "陕西",

        "甘肃省":
            "甘肃",

        "青海省":
            "青海",

        "台湾省":
            "台湾",

        "内蒙古自治区":
            "内蒙古",

        "广西壮族自治区":
            "广西",

        "西藏自治区":
            "西藏",

        "宁夏回族自治区":
            "宁夏",

        "新疆维吾尔自治区":
            "新疆",

        "香港特别行政区":
            "香港",

        "澳门特别行政区":
            "澳门"
    }

    return replace.get(
        name,
        name
    )


# =====================================================
# 从数据中寻找省份
# =====================================================

def find_province_column(
    df
):

    for col in df.columns:

        text = str(col)

        if (
            "地区" in text
            or "省份" in text
            or "省" in text
            or "区域" in text
        ):

            return col

    return df.columns[0]


# =====================================================
# 发病率
# =====================================================

def find_rate_column(
    df
):

    for col in df.columns:

        text = str(col)

        if "发病率" in text:

            return col

    return None


# =====================================================
# 病例数
# =====================================================

def find_cases_column(
    df
):

    for col in df.columns:

        text = str(col)

        if (
            "发病数" in text
            or "病例数" in text
        ):

            return col

    return None


# =====================================================
# 主程序
# =====================================================

def main():

    print(
        "开始生成地图数据..."
    )

    # -----------------------------------------
    # 读取原始数据
    # -----------------------------------------

    df = read_zone_excel()

    print(
        "原始数据列："
    )

    print(
        list(df.columns)
    )

    province_col = (
        find_province_column(
            df
        )
    )

    rate_col = (
        find_rate_column(
            df
        )
    )

    cases_col = (
        find_cases_column(
            df
        )
    )

    print(
        "地区列：",
        province_col
    )

    print(
        "发病率列：",
        rate_col
    )

    print(
        "发病数列：",
        cases_col
    )

    # -----------------------------------------
    # 构建数据
    # -----------------------------------------

    result = {}

    for _, row in df.iterrows():

        province = normalize_name(
            row[province_col]
        )

        if not province:

            continue

        if (
            "全国" in province
            or "合计" in province
        ):

            continue

        rate = 0

        cases = 0

        if rate_col:

            rate = to_number(
                row[rate_col]
            )

        if cases_col:

            cases = to_number(
                row[cases_col]
            )

        result[province] = {

            "value":
                rate,

            "cases":
                cases,

            "deaths":
                0
        }

    # -----------------------------------------
    # 读取中国地图
    # -----------------------------------------

    china_path = os.path.join(
        DATA_DIR,
        "china_base.json"
    )

    with open(
        china_path,
        "r",
        encoding="utf-8"
    ) as f:

        china = json.load(f)

    # -----------------------------------------
    # 合并
    # -----------------------------------------

    for feature in china.get(
        "features",
        []
    ):

        props = feature.setdefault(
            "properties",
            {}
        )

        name = props.get(
            "name",
            ""
        )

        normalized = normalize_name(
            name
        )

        info = result.get(
            normalized,
            {}
        )

        props["name"] = name

        props["value"] = (
            info.get(
                "value",
                0
            )
        )

        props["cases"] = (
            info.get(
                "cases",
                0
            )
        )

        props["deaths"] = (
            info.get(
                "deaths",
                0
            )
        )

    # -----------------------------------------
    # 输出
    # -----------------------------------------

    output = os.path.join(
        OUTPUT_DIR,
        "zone.json"
    )

    with open(
        output,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            china,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        "\n地图数据生成完成："
    )

    print(
        output
    )


if __name__ == "__main__":

    main()