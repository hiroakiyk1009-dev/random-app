import tkinter as tk
from tkinter import messagebox
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

history = []

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

# --- 生成処理 ---
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

    result_text = f"{rand_time}　{rand_age}　{rand_region}"

    history.insert(0, result_text)

    if len(history) > 20:
        history.pop()

    update_history_display()

# --- 履歴表示更新 ---
def update_history_display():
    history_box.delete(0, tk.END)
    for item in history:
        history_box.insert(tk.END, item)

# --- 履歴クリア ---
def clear_history():
    history.clear()
    update_history_display()

# --- GUI ---
root = tk.Tk()
root.title("ランダム生成GUI")
root.geometry("500x500")

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

tk.Button(root, text="生成する", command=generate).pack(pady=5)
tk.Button(root, text="履歴クリア", command=clear_history).pack(pady=5)

tk.Label(root, text="履歴（最大20件）").pack()

history_box = tk.Listbox(root, width=70, height=15)
history_box.pack(pady=10)

root.mainloop()
