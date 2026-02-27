import streamlit as st
import google.generativeai as genai
import random
from PIL import Image
import io
import json
from datetime import datetime

# ==============================
# API設定（無料枠安定構成）
# ==============================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config={
        "temperature": 0.7,
        "top_p": 0.9,
        "max_output_tokens": 1024,
    },
)

st.set_page_config(page_title="AIキャラ生成", layout="wide")

# ==============================
# セッション初期化
# ==============================
if "character" not in st.session_state:
    st.session_state.character = None

# ==============================
# 年齢→生年月日生成
# ==============================
def generate_birthday(age):
    today = datetime.today()
    birth_year = today.year - age
    random_day = datetime(
        birth_year,
        random.randint(1, 12),
        random.randint(1, 28),
    )
    return random_day.strftime("%Y年%m月%d日")

# ==============================
# 画像分析（安定版）
# ==============================
def analyze_image(image):

    prompt = """
この女性の雰囲気を分析してください。
必ずJSON形式のみで出力してください。

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

    # PIL → バイト変換
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="JPEG")
    img_bytes = img_byte_arr.getvalue()

    response = model.generate_content(
        [
            prompt,
            {
                "mime_type": "image/jpeg",
                "data": img_bytes
            }
        ]
    )

    try:
        return json.loads(response.text)
    except:
        return {
            "雰囲気": "不明",
            "推定職業": "不明",
            "推定趣味": "不明",
            "乗っていそうな車": "不明",
            "休日の過ごし方": "不明",
            "婚歴": "不明",
            "使いそうな顔文字": "😊"
        }

# ==============================
# まとめて文章生成（API節約）
# ==============================
def generate_profile_text(profile_prompt):

    full_prompt = f"""
以下の情報をもとに生成してください。

1. 自己紹介文
2. 初対面アタック文
3. AIチャット人格プロンプト

{profile_prompt}
"""

    response = model.generate_content(full_prompt)
    return response.text


# ==============================
# UI
# ==============================
st.title("💖 AI女性キャラ完全自動生成")

uploaded_file = st.file_uploader("画像アップロード", type=["jpg", "png", "jpeg"])

age_option = st.radio("年齢設定", ["ランダム", "自分で指定"])

if age_option == "自分で指定":
    age = st.slider("年齢選択", 20, 70, 35)
else:
    age = random.randint(20, 70)

st.subheader("性格ステータス")

curiosity = st.slider("好奇心", 0, 100, 80)
amae = st.slider("甘え度", 0, 100, 60)
rational = st.slider("理性", 0, 100, 75)
care = st.slider("包容力", 0, 100, 85)
active = st.slider("積極性", 0, 100, 70)

col1, col2 = st.columns(2)

with col1:
    if st.button("✨ キャラ生成"):

        if uploaded_file:

            image = Image.open(uploaded_file)

            analysis = analyze_image(image)
            birthday = generate_birthday(age)

            profile_prompt = f"""
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

            generated_text = generate_profile_text(profile_prompt)

            charamemo = f"""
キャラメモ：
年齢：{age}歳（{birthday}生まれ）
職業：{analysis['推定職業']}
休日：{analysis['休日の過ごし方']}
婚歴：{analysis['婚歴']}
趣味：{analysis['推定趣味']}
車：{analysis['乗っていそうな車']}
"""

            st.session_state.character = {
                "プロフィール": analysis,
                "生成テキスト": generated_text,
                "キャラメモ": charamemo
            }

with col2:
    if st.button("🔄 リセット"):
        st.session_state.character = None

# ==============================
# 表示
# ==============================
if st.session_state.character:

    st.markdown("## 📌 キャラメモ")
    st.code(st.session_state.character["キャラメモ"])

    st.markdown("## 👤 プロフィール")
    st.json(st.session_state.character["プロフィール"])

    st.markdown("## 📝 生成テキスト")
    st.write(st.session_state.character["生成テキスト"])
