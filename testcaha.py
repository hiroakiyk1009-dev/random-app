import streamlit as st
import google.generativeai as genai
import random
from PIL import Image
import json
from datetime import datetime
# ==============================
# API設定
# ==============================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel(
    model_name="models/gemini-2.5-flash",
    generation_config={
        "temperature": 0.9,
        "top_p": 0.95,
        "max_output_tokens": 2048,
    },
)

st.set_page_config(page_title="AIキャラ生成", layout="wide")

# ==============================
# セッション初期化
# ==============================
if "character" not in st.session_state:
    st.session_state.character = None

# ==============================
# 年齢から生年月日逆算
# ==============================
def generate_birthday(age):
    today = datetime.today()
    birth_year = today.year - age
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{birth_year}年{month:02d}月{day:02d}日"

# ==============================
# 画像分析
# ==============================
def analyze_image(image):
    prompt = """
この女性の雰囲気を分析してください。
必ずJSONのみで出力してください。

{
 "雰囲気":"",
 "推定職業":"",
 "推定趣味":"",
 "乗っていそうな車":"",
 "休日の過ごし方":"",
 "婚歴":"",
 "使いそうな顔文字":""
}
"""

    response = model.generate_content([prompt, image])
    text = response.text.strip()

    try:
        return json.loads(text)
    except:
        return {
            "雰囲気": "上品で落ち着いた大人の女性",
            "推定職業": "受付",
            "推定趣味": "旅行・カフェ巡り",
            "乗っていそうな車": "レクサスNX",
            "休日の過ごし方": "週末にゆったり外出",
            "婚歴": "独身",
            "使いそうな顔文字": "✨😊"
        }

# ==============================
# AI文章生成
# ==============================
def generate_text(prompt):
    response = model.generate_content(prompt)
    return response.text.strip()

# ==============================
# UI
# ==============================
st.title("💖 AI女性キャラ完全自動生成")

uploaded_file = st.file_uploader("画像アップロード", type=["jpg","png","jpeg"])

age_option = st.radio("年齢設定", ["ランダム", "自分で指定"])

if age_option == "自分で指定":
    age = st.slider("年齢選択", 20, 70, 35)
else:
    age = random.randint(20,70)

st.subheader("性格ステータス")

curiosity = st.slider("好奇心", 0,100,80)
amae = st.slider("甘え度", 0,100,60)
rational = st.slider("理性", 0,100,75)
care = st.slider("包容力", 0,100,85)
active = st.slider("積極性", 0,100,70)

col1,col2 = st.columns(2)

with col1:
    if st.button("✨ キャラ生成"):
        if not uploaded_file:
            st.warning("画像をアップロードしてください")
        else:
            image = Image.open(uploaded_file)

            analysis = analyze_image(image)
            birthday = generate_birthday(age)

            profile_prompt = f"""
以下の情報をもとに女性プロフィールを作成してください。

年齢:{age}
生年月日:{birthday}
雰囲気:{analysis['雰囲気']}
職業:{analysis['推定職業']}
趣味:{analysis['推定趣味']}
車:{analysis['乗っていそうな車']}
休日:{analysis['休日の過ごし方']}
婚歴:{analysis['婚歴']}
顔文字:{analysis['使いそうな顔文字']}

好奇心:{curiosity}
甘え度:{amae}
理性:{rational}
包容力:{care}
積極性:{active}
"""

            intro = generate_text("自己紹介文を作成してください。\n" + profile_prompt)
            attack = generate_text("初対面アタック文を作成してください。\n" + profile_prompt)
            personality_prompt = generate_text("AIチャット人格プロンプトを作成してください。\n" + profile_prompt)

            charamemo = f"""
キャラメモ：
改行：1行　
口調：敬語　
本名：AI生成　
年齢：{age}歳（{birthday}生まれ）　
職業：{analysis['推定職業']}　
休日：{analysis['休日の過ごし方']}　
婚歴：{analysis['婚歴']}　
顔文字：{analysis['使いそうな顔文字']}　
趣味：{analysis['推定趣味']}　
車：{analysis['乗っていそうな車']}
"""

            st.session_state.character = {
                "プロフィール": analysis,
                "自己紹介": intro,
                "アタック文": attack,
                "AI人格プロンプト": personality_prompt,
                "キャラメモ": charamemo
            }

with col2:
    if st.button("🔄 リセット"):
        st.session_state.character = None
        st.rerun()

# ==============================
# 表示
# ==============================
if st.session_state.character:

    st.markdown("## 📌 キャラメモ")
    st.code(st.session_state.character["キャラメモ"])

    st.markdown("## 👤 プロフィール")
    st.json(st.session_state.character["プロフィール"])

    st.markdown("## 📝 自己紹介")
    st.write(st.session_state.character["自己紹介"])

    st.markdown("## 💌 アタック文")
    st.write(st.session_state.character["アタック文"])

    st.markdown("## 🤖 AI人格プロンプト")
    st.code(st.session_state.character["AI人格プロンプト"])
