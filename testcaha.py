import streamlit as st
import random
import base64
import json
from datetime import datetime, timedelta
from openai import OpenAI

# =============================
# 初期設定
# =============================
st.set_page_config(page_title="AIキャラ生成 完全版", layout="centered")
client = OpenAI()

if "character" not in st.session_state:
    st.session_state.character = None

# =============================
# 年齢→生年月日
# =============================
def generate_birthdate(age):
    today = datetime.today()
    birth_year = today.year - age
    random_day = random.randint(0, 364)
    birth_date = datetime(birth_year, 1, 1) + timedelta(days=random_day)
    return birth_date.strftime("%Y年%m月%d日")

# =============================
# 画像base64化
# =============================
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.read()).decode("utf-8")

# =============================
# 画像分析
# =============================
def analyze_image(image_base64):

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": """
この女性の画像から以下を推測しJSONで出力してください。

{
 "雰囲気": "",
 "休日タイプ": "",
 "婚姻傾向": "",
 "顔文字系統": ""
}
JSONのみ出力。
"""}
,
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        },
                    },
                ],
            }
        ],
        response_format={"type": "json_object"},
    )

    return response.choices[0].message.content

# =============================
# AIプロフィール生成
# =============================
def generate_ai_profile(base_data):

    prompt = f"""
以下情報を元に女性プロフィールをJSONで生成。

入力:
{base_data}

出力形式:
{{
 "名前":"",
 "ふりがな":"",
 "血液型":"",
 "身長":"",
 "性格":"",
 "趣味":"",
 "職業":"",
 "車":""
}}

JSONのみ出力。
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.9,
        response_format={"type": "json_object"}
    )

    return response.choices[0].message.content

# =============================
# AI文章生成
# =============================
def generate_ai_text(full_profile):

    prompt = f"""
以下プロフィールから生成してください。

{full_profile}

出力形式:
{{
 "自己紹介":"",
 "アタック文":"",
 "AI人格プロンプト":""
}}

JSONのみ出力。
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.9,
        response_format={"type": "json_object"}
    )

    return response.choices[0].message.content

# =============================
# キャラメモ生成（Python固定）
# =============================
def build_character_memo(profile, image_analysis):

    emoji_map = {
        "大人系": "✨🌹💋",
        "可愛い系": "😊🌸💕",
        "ギャル系": "😘👌🔥",
        "癒し系": "🌷😊☕"
    }

    holiday = image_analysis.get("休日タイプ", "週末")
    marriage_type = image_analysis.get("婚姻傾向", "独身寄り")

    if marriage_type == "既婚寄り":
        marriage = "既婚（内緒）"
    elif marriage_type == "バツあり寄り":
        marriage = "バツ1"
    else:
        marriage = "独身"

    emoji = emoji_map.get(image_analysis.get("顔文字系統", ""), "😊")

    memo = f"""キャラメモ：
改行：1行　口調：敬語　本名：{profile['名前']}（{profile['ふりがな']}）　年齢：{profile['年齢']}歳（{profile['生年月日']}生まれ、{profile['血液型']}型）職業：{profile['職業']}　休日：{holiday}　婚歴：{marriage}　顔文字：{emoji}　趣味：{profile['趣味']}車：{profile['車']}　写メ⇒https://example.com"""

    return memo

# =============================
# UI
# =============================
st.title("🔥 AIキャラ生成 完全統合版")

uploaded_file = st.file_uploader("女性画像アップロード", type=["jpg","jpeg","png"])

age_input = st.number_input("年齢（20〜70）", 20, 70, 35)

st.subheader("🎛 性格パラメータ")
curiosity = st.slider("好奇心", 0, 100, 80)
amae = st.slider("甘え度", 0, 100, 60)
reason = st.slider("理性", 0, 100, 75)
tolerance = st.slider("包容力", 0, 100, 85)
active = st.slider("積極性", 0, 100, 70)

# =============================
# 生成処理
# =============================
if st.button("✨ 生成開始"):

    age = age_input
    birthdate = generate_birthdate(age)

    base_data = {
        "年齢": age,
        "生年月日": birthdate,
        "好奇心": curiosity,
        "甘え度": amae,
        "理性": reason,
        "包容力": tolerance,
        "積極性": active
    }

    if uploaded_file:
        image_base64 = encode_image(uploaded_file)
        image_analysis = json.loads(analyze_image(image_base64))
    else:
        image_analysis = {"休日タイプ":"週末","婚姻傾向":"独身寄り","顔文字系統":"癒し系"}

    ai_profile = json.loads(generate_ai_profile(base_data))

    ai_profile["年齢"] = age
    ai_profile["生年月日"] = birthdate

    full_profile = {**ai_profile, **base_data}

    ai_text = json.loads(generate_ai_text(full_profile))

    memo = build_character_memo(ai_profile, image_analysis)

    st.session_state.character = {
        "プロフィール": ai_profile,
        "自己紹介": ai_text["自己紹介"],
        "アタック文": ai_text["アタック文"],
        "AI人格プロンプト": ai_text["AI人格プロンプト"],
        "キャラメモ": memo
    }

# =============================
# 表示
# =============================
if st.session_state.character:

    st.subheader("📄 プロフィール")
    st.json(st.session_state.character["プロフィール"])

    st.markdown("### 📝 自己紹介")
    st.write(st.session_state.character["自己紹介"])

    st.markdown("### 💌 アタック文")
    st.write(st.session_state.character["アタック文"])

    st.markdown("### 🤖 AI人格プロンプト")
    st.code(st.session_state.character["AI人格プロンプト"])

    st.markdown("### 🧠 キャラメモ")
    st.text(st.session_state.character["キャラメモ"])

# =============================
# 再作成
# =============================
if st.button("🔄 再作成"):
    st.session_state.character = None
    st.rerun()

# =============================
# 完全リセット
# =============================
if st.button("🧹 完全リセット"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
