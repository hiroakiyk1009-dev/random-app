import streamlit as st
import google.generativeai as genai
import random
from PIL import Image
import io
import json
from datetime import datetime

# ==============================
# API設定（無料枠安定）
# ==============================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel(
    "models/gemini-2.5-flash",
    generation_config={
        "temperature": 0.85,
        "top_p": 0.9,
        "max_output_tokens": 800,
        "response_mime_type": "application/json"  # JSON固定
    },
)

st.set_page_config(page_title="AIキャラ生成", layout="wide")

if "character" not in st.session_state:
    st.session_state.character = None

# ==============================
# 生年月日生成
# ==============================
def generate_birthday(age):
    today = datetime.today()
    birth_year = today.year - age
    random_day = datetime(
        birth_year,
        random.randint(1, 12),
        random.randint(1, 28)
    )
    return random_day.strftime("%Y年%m月%d日")

# ==============================
# 画像分析（JSON強制）
# ==============================
def analyze_image(image):

    prompt = """
以下のキーのみを含むJSONのみを出力せよ。
説明文・前置き・補足は禁止。

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
            "雰囲気": "落ち着いた大人の女性",
            "推定職業": "会社員",
            "推定趣味": "カフェ巡り",
            "乗っていそうな車": "レクサスNX",
            "休日の過ごし方": "ショッピング",
            "婚歴": "独身",
            "使いそうな顔文字": "😊"
        }

# ==============================
# UI
# ==============================
st.title("💖 AI女性キャラ完全自動生成")

uploaded_file = st.file_uploader("画像アップロード", type=["jpg","png","jpeg"])

age_option = st.radio("年齢設定", ["ランダム", "自分で指定"])

if age_option == "自分で指定":
    age = st.slider("年齢選択", 20, 70, 35)
else:
    age = random.randint(20, 70)

st.subheader("🎛 性格パラメータ")

curiosity = st.slider("好奇心", 0,100,80)
amae = st.slider("甘え度", 0,100,60)
rational = st.slider("理性", 0,100,75)
care = st.slider("包容力", 0,100,85)
active = st.slider("積極性", 0,100,70)

col1, col2 = st.columns(2)

# ==============================
# 生成
# ==============================
with col1:
    if st.button("✨ キャラ生成"):

        if not uploaded_file:
            st.warning("画像をアップロードしてください")
        else:
            image = Image.open(uploaded_file)
            analysis = analyze_image(image)
            birthday = generate_birthday(age)

            charamemo = f"""キャラメモ：
改行：1行　口調：敬語　本名：AI生成
年齢：{age}歳（{birthday}生まれ）
職業：{analysis['推定職業']}
休日：{analysis['休日の過ごし方']}
婚歴：{analysis['婚歴']}
顔文字：{analysis['使いそうな顔文字']}
趣味：{analysis['推定趣味']}
車：{analysis['乗っていそうな車']}
"""

            st.session_state.character = {
                "キャラメモ": charamemo
            }

# ==============================
# リセット
# ==============================
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
