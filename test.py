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

# 「選択モード」
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

# ここは「現在の実際の話し方」ではなく「選択モード」を保持する
if "speech_mode" not in st.session_state:
    st.session_state.speech_mode = "敬語"

if "used_ages" not in st.session_state:
    st.session_state.used_ages = []

# ==============================
# 関数
# ==============================
def to_fullwidth_colon(text: str) -> str:
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
        available = all_ages[:]
        if exclude:
            available = [a for a in available if a != exclude]

    selected = random.choice(available)
    st.session_state.used_ages.append(selected)
    return selected

def random_region():
    return random.choices(regions, weights=region_weights)[0]

def parse_code(text):
    if not text:
        return ""
    m = re.search(r"(\d{4})", text)
    return m.group(1) if m else ""

def resolve_speech(mode: str) -> str:
    """生成時に実際の話し方を決定する"""
    if mode == "ランダム":
        return random.choice(["敬語", "タメ語"])
    return mode

def format_output(category, code, time_str, age_str, region_str, speech, typ):
    register_text = f"登録〜{code}" if code else ""
    register_time = "0：00" if code else ""

    parts = [
        f"【{category}】",
        code,
        time_str,
        age_str,
        region_str,
        speech,
        typ,
        register_text,
        register_time,
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

code_raw = st.text_input("＜0228用＞コード入力（任意）", placeholder="例：＜0228用＞")
code = parse_code(code_raw)

selected_category = st.radio("用途", categories, horizontal=True)

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

st.write(f"現在設定：**{st.session_state.speech_mode}**")

selected_type = st.selectbox("系統", types, index=0)

selected_time = st.radio(
    "時間枠",
    options=list(time_ranges.keys()),
    format_func=lambda x: f"{time_ranges[x][0]}〜{time_ranges[x][1]}"
)

# ==============================
# 生成ボタン
# ==============================
btn1, btn2 = st.columns(2)

with btn1:
    if st.button("生成する"):
        start, end = time_ranges[selected_time]

        t = random_time(start, end)
        a = random_age()
        r = random_region()

        # ここで毎回、現在モードから実際の話し方を決める
        actual_speech = resolve_speech(st.session_state.speech_mode)

        text = format_output(
            selected_category,
            code,
            t,
            a,
            r,
            actual_speech,
            selected_type
        )

        st.session_state.last = {
            "time": t,
            "age": a,
            "region": r,
            "category": selected_category,
            "speech": actual_speech,          # 実際に生成された値を保存
            "speech_mode": st.session_state.speech_mode,  # モードも保存
            "type": selected_type,
            "code": code
        }

        add_history(text)

with btn2:
    if st.button("年齢だけチェンジ"):
        if st.session_state.last:
            l = st.session_state.last

            t = l["time"]
            r = l["region"]
            c = l["category"]
            typ = l["type"]
            code_keep = l["code"]

            a = random_age(exclude=l["age"])

            # ここでも「現在のモード」を見て再抽選
            actual_speech = resolve_speech(st.session_state.speech_mode)

            text = format_output(
                c,
                code_keep,
                t,
                a,
                r,
                actual_speech,
                typ
            )

            st.session_state.last = {
                "time": t,
                "age": a,
                "region": r,
                "category": c,
                "speech": actual_speech,
                "speech_mode": st.session_state.speech_mode,
                "type": typ,
                "code": code_keep
            }

            add_history(text)
        else:
            st.warning("先に生成してください")

# ==============================
# 履歴 / お気に入り
# ==============================
left, right = st.columns([4, 2])

with left:
    st.subheader("履歴")
    for i, item in enumerate(st.session_state.history):
        row_left, row_right = st.columns([8, 1])

        with row_left:
            st.write(item)

        with row_right:
            if st.button("★", key=f"fav_{i}"):
                if item not in st.session_state.favorites:
                    st.session_state.favorites.append(item)

with right:
    st.subheader("気に入ったもの")
    if st.session_state.favorites:
        for fav in st.session_state.favorites:
            st.write(fav)
    else:
        st.write("まだありません")

    if st.button("お気に入りクリア"):
        st.session_state.favorites = []

# ==============================
# 直近生成
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
else:
    st.write("まだ生成されていません")

# ==============================
# クリア
# ==============================
clear1, clear2 = st.columns(2)

with clear1:
    if st.button("履歴クリア"):
        st.session_state.history = []
        st.session_state.last = None
        st.session_state.used_ages = []

with clear2:
    if st.button("全クリア"):
        st.session_state.history = []
        st.session_state.favorites = []
        st.session_state.last = None
        st.session_state.used_ages = []
        st.session_state.speech_mode = "敬語"
