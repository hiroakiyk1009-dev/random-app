import streamlit as st
import random
import re
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

# 表示を「近隣１」みたいにしたいので、最初から全角で持つ
regions = ["完全一緒", "近隣１", "近隣２", "近隣３"]
region_weights = [44, 44, 10, 2]

# 用途カテゴリ
categories = ["マッチル", "出会いチャット", "パートナー"]

# 話し方
speech_styles = ["敬語", "タメ語"]

# 系統（ノーマル固定にしてたけど、例で「⚠️来月アポ系」が出てるので追加）
types = ["ノーマル系", "⚠️来月アポ系"]

# ==============================
# セッション初期化
# ==============================
if "history" not in st.session_state:
    st.session_state.history = []

if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "last" not in st.session_state:
    st.session_state.last = None
    # {"time":..., "age":..., "region":..., "category":..., "speech":..., "type":..., "code":...}

# ==============================
# ユーティリティ
# ==============================
def to_fullwidth_colon(t: str) -> str:
    # "9:48" -> "9：48"
    return t.replace(":", "：")

def random_time(start, end):
    fmt = "%H:%M"
    start_dt = datetime.strptime(start, fmt)
    end_dt = datetime.strptime("23:59", fmt) if end == "24:00" else datetime.strptime(end, fmt)
    delta = end_dt - start_dt
    result = start_dt + timedelta(minutes=random.randint(0, int(delta.total_seconds() // 60)))
    return result.strftime("%H:%M")

def random_age():
    g = random.choice(list(age_groups.keys()))
    return random.choice(age_groups[g])

def random_region():
    return random.choices(regions, weights=region_weights)[0]

def parse_mmdd_code(raw: str) -> str:
    """
    例:
      "<0228用>" -> "0228"
      "0228" -> "0228"
      "＜0228用＞" -> "0228"
    それ以外 -> ""
    """
    if not raw:
        return ""
    m = re.search(r"(\d{4})", raw)
    return m.group(1) if m else ""

def format_text(category, code, time_str, age_str, region_str, speech, typ):
    # 登録〜MMDD と 0：00 と 最後の空白欄
    reg = f"登録〜{code}" if code else ""
    reg_time = "0：00" if code else ""
    last_blank = ""  # ここは空白（表示しない）

    # 「コード」を必ず2番目に出す（未入力なら空欄として出す）
    # 末尾の空白欄も含めて、区切りは全角スペース（見た目合わせ）
    parts = [
        f"【{category}】",
        code,
        to_fullwidth_colon(time_str),
        age_str,
        region_str,
        speech,
        typ,
        reg,
        reg_time,
        last_blank,
    ]

    # 連続空欄があっても並びを維持したいので、そのまま結合
    return "　".join(parts)

def add_history(category, code, time_str, age_str, region_str, speech, typ):
    text = format_text(category, code, time_str, age_str, region_str, speech, typ)
    st.session_state.history.insert(0, text)
    if len(st.session_state.history) > 20:
        st.session_state.history.pop()

# ==============================
# UI
# ==============================
st.title("ランダム生成アプリ")

# ★追加：＜0228用＞の入力欄
raw_code = st.text_input("＜MMDD用＞（任意）", placeholder="例：＜0228用＞ または 0228")
code = parse_mmdd_code(raw_code)

# 1) 用途
selected_category = st.radio("用途を選択", categories, horizontal=True)

# 2) 話し方
selected_speech = st.radio("話し方を選択", speech_styles, horizontal=True)

# 3) 系統
selected_type = st.selectbox("系統を選択", types, index=0)

# 4) 時間枠
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
            "category": c, "speech": s, "type": typ,
            "code": code,
        }

        add_history(c, code, t, a, r, s, typ)

with btn2:
    if st.button("年齢だけチェンジ"):
        if st.session_state.last:
            # 時間・地域・用途・話し方・系統・コードは保持、年齢だけ再抽選
            t = st.session_state.last["time"]
            r = st.session_state.last["region"]
            c = st.session_state.last["category"]
            s = st.session_state.last["speech"]
            typ = st.session_state.last["type"]
            code_keep = st.session_state.last.get("code", "")

            a = random_age()

            st.session_state.last = {
                "time": t, "age": a, "region": r,
                "category": c, "speech": s, "type": typ,
                "code": code_keep,
            }

            add_history(c, code_keep, t, a, r, s, typ)
        else:
            st.warning("先に生成してください")

# ==============================
# 履歴 ＋ お気に入り
# ==============================
left, right = st.columns(2)

with left:
    st.subheader("履歴（最大20件）")
    for i, item in enumerate(st.session_state.history):
        c1, c2 = st.columns([6, 1])
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
    st.write(format_text(l["category"], l.get("code", ""), l["time"], l["age"], l["region"], l["speech"], l["type"]))
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
