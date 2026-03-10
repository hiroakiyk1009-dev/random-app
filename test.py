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
speech_modes = ["敬語", "タメ語", "ランダム"]

# ==============================
# セッション
# ==============================
if "history" not in st.session_state:
    st.session_state.history = []

if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "last" not in st.session_state:
    st.session_state.last = None

if "speech_mode" not in st.session_state:
    st.session_state.speech_mode = "敬語"

if "used_ages" not in st.session_state:
    st.session_state.used_ages = []

# ==============================
# 関数
# ==============================

def to_fullwidth_colon(text):
    return text.replace(":", "：")

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

    return to_fullwidth_colon(result.strftime("%H:%M"))

def get_all_ages():
    all_ages = []
    for group in age_groups.values():
        all_ages.extend(group)
    return all_ages

def random_age(exclude=None):
    all_ages = get_all_ages()

    available = [a for a in all_ages if a not in st.session_state.used_ages]

    if exclude:
        available = [a for a in available if a != exclude]

    if not available:
        st.session_state.used_ages = []
        available = all_ages

    selected = random.choice(available)
    st.session_state.used_ages.append(selected)

    return selected

def random_region():
    return random.choices(regions, weights=region_weights)[0]

def parse_code(text):
    if not text:
        return ""
    m = re.search(r"\d{4}", text)
    return m.group(0) if m else ""

def get_speech():
    mode = st.session_state.speech_mode

    if mode == "ランダム":
        return random.choice(["敬語", "タメ語"])

    return mode

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

def add_history(text):
    st.session_state.history.insert(0, text)

    if len(st.session_state.history) > 20:
        st.session_state.history.pop()

# ==============================
# UI
# ==============================

st.title("ランダム生成アプリ")

code_raw = st.text_input("＜0228用＞コード入力（任意）")
code = parse_code(code_raw)

category = st.radio("用途", categories, horizontal=True)

st.subheader("話し方")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("敬語"):
        st.session_state.speech_mode = "敬語"

with col2:
    if st.button("タメ語"):
        st.session_state.speech_mode = "タメ語"

with col3:
    if st.button("ランダム"):
        st.session_state.speech_mode = "ランダム"

st.write("現在設定：", st.session_state.speech_mode)

typ = st.selectbox("系統", types)

selected_time = st.radio(
    "時間枠",
    options=list(time_ranges.keys()),
    format_func=lambda x: f"{time_ranges[x][0]}〜{time_ranges[x][1]}"
)

# ==============================
# 生成ボタン
# ==============================

b1, b2 = st.columns(2)

with b1:

    if st.button("生成する"):

        start, end = time_ranges[selected_time]

        t = random_time(start, end)
        a = random_age()
        r = random_region()

        speech = get_speech()

        text = format_output(category, code, t, a, r, speech, typ)

        st.session_state.last = {
            "time": t,
            "age": a,
            "region": r,
            "category": category,
            "speech": speech,
            "type": typ,
            "code": code
        }

        add_history(text)

with b2:

    if st.button("年齢だけチェンジ"):

        if st.session_state.last:

            l = st.session_state.last

            t = l["time"]
            r = l["region"]
            c = l["category"]
            typ = l["type"]
            code_keep = l["code"]

            speech = get_speech()

            a = random_age(exclude=l["age"])

            text = format_output(c, code_keep, t, a, r, speech, typ)

            add_history(text)

# ==============================
# 履歴 / お気に入り
# ==============================

left, right = st.columns([4,2])

with left:

    st.subheader("履歴")

    for i, item in enumerate(st.session_state.history):

        c1, c2 = st.columns([8,1])

        with c1:
            st.write(item)

        with c2:
            if st.button("★", key=f"fav{i}"):

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

c1, c2 = st.columns(2)

with c1:
    if st.button("履歴クリア"):
        st.session_state.history = []
        st.session_state.used_ages = []

with c2:
    if st.button("全クリア"):
        st.session_state.history = []
        st.session_state.favorites = []
        st.session_state.last = None
        st.session_state.used_ages = []
        st.session_state.speech_mode = "敬語"
