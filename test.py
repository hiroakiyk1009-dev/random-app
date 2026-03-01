import streamlit as st
import random
from datetime import datetime, timedelta

# --- データ ---
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

regions = ["完全一緒", "近隣1", "近隣2", "近隣3"]
region_weights = [44, 44, 10, 2]

# 用途カテゴリ
categories = ["マッチル", "出会いチャット", "パートナー"]

# 話し方
speech_styles = ["敬語", "タメ語"]

# 系統（今はノーマル固定で選択できるように）
types = ["ノーマル系"]  # 将来増やすならここに追加

# ==============================
# セッション初期化
# ==============================
if "history" not in st.session_state:
    st.session_state.history = []

if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "last" not in st.session_state:
    st.session_state.last = None  # {"time":..., "age":..., "region":..., "category":..., "speech":..., "type":...}

# ==============================
# ユーティリティ
# ==============================
def random_time(start, end):
    fmt = "%H:%M"
    start_dt = datetime.strptime(start, fmt)
    end_dt = datetime.strptime("23:59", fmt) if end == "24:00" else datetime.strptime(end, fmt)
    delta = end_dt - start_dt
    return (start_dt + timedelta(minutes=random.randint(0, int(delta.total_seconds() // 60)))).strftime("%H:%M")

def random_age():
    g = random.choice(list(age_groups.keys()))
    return random.choice(age_groups[g])

def random_region():
    return random.choices(regions, weights=region_weights)[0]

def format_text(category, time_str, age_str, region_str, speech, typ):
    # 指定フォーマット：
    # 【パートナー】　12：47　65〜69歳　完全一緒　敬語　ノーマル系
    return f"【{category}】　{time_str}　{age_str}　{region_str}　{speech}　{typ}"

def add_history(category, time_str, age_str, region_str, speech, typ):
    text = format_text(category, time_str, age_str, region_str, speech, typ)
    st.session_state.history.insert(0, text)
    if len(st.session_state.history) > 20:
        st.session_state.history.pop()

# ==============================
# UI
# ==============================
st.title("ランダム生成アプリ")

# 1) 用途選択
selected_category = st.radio("用途を選択", categories, horizontal=True)

# 2) 話し方選択
selected_speech = st.radio("話し方を選択", speech_styles, horizontal=True)

# 3) 系統選択（ノーマル固定で選べるように）
selected_type = st.selectbox("系統を選択", types, index=0)

# 時間枠選択
selected_time = st.radio(
    "時間枠を1つ選択（必須）",
    options=list(time_ranges.keys()),
    format_func=lambda x: f"{time_ranges[x][0]}〜{time_ranges[x][1]}"
)

btn1, btn2 = st.columns(2)

with btn1:
    if st.button("生成する"):
        start, end = time_ranges[selected_time]
        t = random_time(start, end)
        a = random_age()
        r = random_region()

        c = selected_category
        s = selected_speech
        typ = selected_type

        st.session_state.last = {
            "time": t, "age": a, "region": r,
            "category": c, "speech": s, "type": typ
        }

        add_history(c, t, a, r, s, typ)

with btn2:
    if st.button("年齢だけチェンジ"):
        if st.session_state.last:
            # 時間・地域・用途・話し方・系統は保持、年齢だけ再抽選
            t = st.session_state.last["time"]
            r = st.session_state.last["region"]
            c = st.session_state.last["category"]
            s = st.session_state.last["speech"]
            typ = st.session_state.last["type"]

            a = random_age()

            st.session_state.last = {
                "time": t, "age": a, "region": r,
                "category": c, "speech": s, "type": typ
            }

            add_history(c, t, a, r, s, typ)
        else:
            st.warning("先に生成してください")

# ==============================
# メイン表示（履歴 ＋ お気に入り）
# ==============================
left, right = st.columns(2)

with left:
    st.subheader("履歴（最大20件）")
    for i, item in enumerate(st.session_state.history):
        c1, c2 = st.columns([5, 1])
        with c1:
            st.write(item)
        with c2:
            if st.button("★", key=f"fav_{i}"):
                if item not in st.session_state.favorites:
                    st.session_state.favorites.append(item)

with right:
    st.subheader("⭐ 気に入ったもの")
    if st.session_state.favorites:
        for fav in st.session_state.favorites:
            st.write(fav)
    else:
        st.write("まだありません")

    if st.button("⭐ クリア"):
        st.session_state.favorites = []

# ==============================
# 直近結果
# ==============================
st.subheader("直近の結果")
if st.session_state.last:
    l = st.session_state.last
    st.write(format_text(l["category"], l["time"], l["age"], l["region"], l["speech"], l["type"]))
else:
    st.write("まだ生成されていません")

# ==============================
# クリア系
# ==============================
col_clear1, col_clear2 = st.columns(2)
with col_clear1:
    if st.button("履歴クリア"):
        st.session_state.history = []
        st.session_state.last = None

with col_clear2:
    if st.button("お気に入りも含め全クリア"):
        st.session_state.history = []
        st.session_state.favorites = []
        st.session_state.last = None
