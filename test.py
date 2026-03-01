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

# ==============================
# セッション初期化
# ==============================
if "history" not in st.session_state:
    st.session_state.history = []

# 直近生成を保持する入れ物（時間・地域・年齢）
if "last" not in st.session_state:
    st.session_state.last = None

# --- ランダム時間生成 ---
def random_time(start, end):
    fmt = "%H:%M"
    start_dt = datetime.strptime(start, fmt)

    if end == "24:00":
        end_dt = datetime.strptime("23:59", fmt)
    else:
        end_dt = datetime.strptime(end, fmt)

    delta = end_dt - start_dt
    random_minute = random.randint(0, int(delta.total_seconds() // 60))
    result = start_dt + timedelta(minutes=random_minute)
    return result.strftime("%H:%M")

def random_age():
    age_group = random.choice(list(age_groups.keys()))
    return random.choice(age_groups[age_group])

def random_region():
    return random.choices(regions, weights=region_weights)[0]

def add_history(time_str, age_str, region_str):
    result_text = f"{time_str}　{age_str}　{region_str}"
    st.session_state.history.insert(0, result_text)
    if len(st.session_state.history) > 20:
        st.session_state.history.pop()

# --- 画面 ---
st.title("ランダム生成アプリ")

selected_time = st.radio(
    "時間枠を1つ選択（必須）",
    options=list(time_ranges.keys()),
    format_func=lambda x: f"{time_ranges[x][0]}〜{time_ranges[x][1]}"
)

col1, col2 = st.columns(2)

# ==============================
# ① 通常生成（時間・年齢・地域すべて生成）
# ==============================
with col1:
    if st.button("生成する"):
        start, end = time_ranges[selected_time]
        t = random_time(start, end)
        a = random_age()
        r = random_region()

        # 直近生成を保持
        st.session_state.last = {"time": t, "age": a, "region": r}

        add_history(t, a, r)

# ==============================
# ② 年齢だけチェンジ（時間と地域は保持）
# ==============================
with col2:
    if st.button("年齢だけチェンジ"):
        if st.session_state.last is None:
            st.warning("先に「生成する」を押して、1回生成してください。")
        else:
            t = st.session_state.last["time"]      # 保持
            r = st.session_state.last["region"]    # 保持
            a = random_age()                       # 年齢だけ再抽選

            # 直近生成を更新（時間・地域はそのまま、年齢だけ更新）
            st.session_state.last = {"time": t, "age": a, "region": r}

            add_history(t, a, r)

# ==============================
# 直近の結果表示（分かりやすく）
# ==============================
st.subheader("直近の結果")
if st.session_state.last:
    st.write(f"{st.session_state.last['time']}　{st.session_state.last['age']}　{st.session_state.last['region']}")
else:
    st.write("まだ生成されていません")

# ==============================
# 履歴表示
# ==============================
st.subheader("履歴（最大20件）")
for item in st.session_state.history:
    st.write(item)

if st.button("履歴クリア"):
    st.session_state.history = []
    st.session_state.last = None
