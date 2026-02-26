import tkinter as tk
from tkinter import messagebox
import random
from datetime import datetime, timedelta

# --- データ ---
time_ranges = {
    1: ("8:00", "10:30"),
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

# --- ボタン処理 ---
def generate():
    selected = [i+1 for i, var in enumerate(time_vars) if var.get()]
    
    if len(selected) != 1:
        messagebox.showerror("エラー", "時間枠を1つ選択してください（必須）")
        return
    
    time_key = selected[0]
    start, end = time_ranges[time_key]
    rand_time = random_time(start, end)

    age_group = random.choice(list(age_groups.keys()))
    rand_age = random.choice(age_groups[age_group])

    rand_region = random.choices(regions, weights=region_weights)[0]

    now = datetime.now().strftime("%m月%d日 %H:%M")

    result_label.config(
        text=f"{now}\n{rand_time}　{rand_age}　{rand_region}"
    )

# --- GUI作成 ---
root = tk.Tk()
root.title("ランダム生成GUI")
root.geometry("350x400")

tk.Label(root, text="時間枠を選択（必須）").pack()

time_vars = []
for i in range(1, 6):
    var = tk.BooleanVar()
    time_vars.append(var)
    tk.Checkbutton(
        root,
        text=f"{time_ranges[i][0]}〜{time_ranges[i][1]}",
        variable=var
    ).pack(anchor="w")

tk.Button(root, text="生成する", command=generate).pack(pady=10)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=20)

root.mainloop()
