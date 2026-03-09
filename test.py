import streamlit as st
import random
import re
from datetime import datetime, timedelta

# ==============================
# データ
# ==============================

time_ranges = {
    1: ("8:15", "10:30"),
    2: ("10:31", "13:30"),
    3: ("13:31", "16:30"),
    4: ("16:31", "19:00"),
    5: ("19:01", "24:00"),
}

age_groups = {
    1: ["20歳未満", "20〜24歳", "25〜29歳"],
    2: ["30〜34歳", "35〜39歳"],
    3: ["40〜44歳", "45〜49歳"],
    4: ["50〜54歳", "55〜59歳"],
    5: ["60〜64歳", "65〜69歳", "70歳以上"],
}

regions = ["完全一緒", "近隣１", "近隣２", "近隣３"]
region_weights = [44, 44, 10, 2]

categories = ["マッチル", "出会いチャット", "パートナー"]

types = ["ノーマル系", "⚠️来月アポ系"]

# ==============================
# セッション
# ==============================

if "history" not in st.session_state:
    st.session_state.history = []

if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "last" not in st.session_state:
    st.session_state.last = None

if "speech_style" not in st.session_state:
    st.session_state.speech_style = "敬語"

# ==============================
# 関数
# ==============================

def random_time(start, end):
    fmt = "%H:%M"
    start_dt = datetime.strptime(start, fmt)

    if end == "24:00":
        end_dt = datetime.strptime("23:59", fmt)
    else:
        end_dt = datetime.strptime(end, fmt)

    delta = end_dt - start_dt
    rand = random.randint(0, int(delta.total_seconds() // 60))
    result = start_dt + timedelta(minutes=rand)

    return result.strftime("%H:%M").replace(":", "：")

def random_age():
    g = random.choice(list(age_groups.keys()))
    return random.choice(age_groups[g])

def random_region():
    return random.choices(regions, weights=region_weights)[0]

def parse_code(text):
    if not text:
        return ""
    m = re.search(r"\d{4}", text)
    return m.group(0) if m else ""

def format_output(cat, code, time, age, region, speech, typ):

    reg = f"登録〜{code}" if code else ""
    reg_time = "0：00" if code else ""

    parts = [
        f"【{cat}】",
        code,
        time,
        age,
        region,
        speech,
        typ,
        reg,
        reg_time,
        ""
    ]

    return "　".join(parts)

# ==============================
# UI
# ==============================

st.title("ランダム生成アプリ")

code_raw = st.text_input("＜0228用＞コード入力（任意）")
code = parse_code(code_raw)

# 用途
category = st.radio("用途", categories, horizontal=True)

# 話し方
st.subheader("話し方")

c1,c2,c3 = st.columns(3)

with c1:
    if st.button("敬語"):
        st.session_state.speech_style = "敬語"

with c2:
    if st.button("タメ語"):
        st.session_state.speech_style = "タメ語"

with c3:
    if st.button("ランダム"):
        st.session_state.speech_style = random.choice(["敬語","タメ語"])

speech = st.session_state.speech_style

st.write("現在:", speech)

# 系統
typ = st.selectbox("系統", types)

# 時間枠
selected_time = st.radio(
    "時間枠",
    options=list(time_ranges.keys()),
    format_func=lambda x: f"{time_ranges[x][0]}〜{time_ranges[x][1]}"
)

# ==============================
# ボタン
# ==============================

b1,b2 = st.columns(2)

with b1:
    if st.button("生成する"):

        start,end = time_ranges[selected_time]

        t = random_time(start,end)
        a = random_age()
        r = random_region()

        st.session_state.last = {
            "time":t,
            "age":a,
            "region":r,
            "category":category,
            "speech":speech,
            "type":typ,
            "code":code
        }

        text = format_output(category,code,t,a,r,speech,typ)

        st.session_state.history.insert(0,text)

        if len(st.session_state.history) > 20:
            st.session_state.history.pop()

with b2:
    if st.button("年齢だけチェンジ"):

        if st.session_state.last:

            l = st.session_state.last

            t = l["time"]
            r = l["region"]
            c = l["category"]
            s = l["speech"]
            typ = l["type"]
            code_keep = l["code"]

            a = random_age()

            text = format_output(c,code_keep,t,a,r,s,typ)

            st.session_state.history.insert(0,text)

            if len(st.session_state.history) > 20:
                st.session_state.history.pop()

# ==============================
# 履歴 & お気に入り
# ==============================

left,right = st.columns([4,2])

with left:

    st.subheader("履歴")

    for i,item in enumerate(st.session_state.history):

        c1,c2 = st.columns([8,1])

        with c1:
            st.write(item)

        with c2:
            if st.button("★",key=f"fav{i}"):

                if item not in st.session_state.favorites:
                    st.session_state.favorites.append(item)

with right:

    st.subheader("気に入ったもの")

    for fav in st.session_state.favorites:
        st.write(fav)

    if st.button("お気に入りクリア"):
        st.session_state.favorites = []

# ==============================
# 直近結果
# ==============================

st.subheader("直近生成")

if st.session_state.last:

    l = st.session_state.last

    st.write(
        format_output(
            l["category"],
            l["code"],
            l["time"],
            l["age"],
            l["region"],
            l["speech"],
            l["type"]
        )
    )

# ==============================
# クリア
# ==============================

c1,c2 = st.columns(2)

with c1:
    if st.button("履歴クリア"):
        st.session_state.history = []

with c2:
    if st.button("全クリア"):
        st.session_state.history = []
        st.session_state.favorites = []
        st.session_state.last = None
