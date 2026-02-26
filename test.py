import streamlit as st
import random
from datetime import datetime, timedelta

st.title("ランダム生成アプリ")

time_ranges = {
    "8:00〜10:30": ("8:00", "10:30"),
    "10:31〜13:30": ("10:31", "13:30"),
    "13:31〜16:30": ("13:31", "16:30"),
    "16:31〜19:00": ("16:31", "19:00"),
    "19:01〜24:00": ("19:01", "24:00"),
}

age_groups = [
    "20歳未満","20〜24歳","25〜29歳",
    "30〜34歳","35〜39歳",
    "40〜44歳","45〜49歳",
    "50〜54歳","55〜59歳",
    "60〜64歳","65〜69歳","70歳以上"
]

regions = ["完全一緒", "近隣1", "近隣2", "近隣3"]
weights = [44, 44, 10, 2]

selected_time = st.radio("時間枠を選択（必須）", list(time_ranges.keys()))

def random_time(start, end):
    fmt = "%H:%M"
    start_dt = datetime.strptime(start, fmt)
    end_dt = datetime.strptime("23:59" if end=="24:00" else end, fmt)
    delta = end_dt - start_dt
    random_minute = random.randint(0, int(delta.total_seconds() // 60))
    result = start_dt + timedelta(minutes=random_minute)
    return result.strftime("%H:%M")

if st.button("生成する"):
    start, end = time_ranges[selected_time]
    rand_time = random_time(start, end)
    rand_age = random.choice(age_groups)
    rand_region = random.choices(regions, weights=weights)[0]
    now = datetime.now().strftime("%m月%d日 %H:%M")

    st.success(f"{now}\n{rand_time}　{rand_age}　{rand_region}")
