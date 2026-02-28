import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from PIL import Image
import streamlit as st
import os

# ==========================
# APIキー設定
# ==========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.5-flash")

# ==========================
# 雰囲気レベル変換
# ==========================
def tone_level_to_text(level: int):
    tone_map = {
        1: "非常に落ち着き重視。感情表現は最小限。",
        2: "やや控えめ。上品で穏やか。",
        3: "自然で親しみやすい標準的な表現。",
        4: "感情豊かで柔らかい表現。",
        5: "かなり感情豊かで印象的。"
    }
    return tone_map.get(level, tone_map[3])

def sexiness_to_text(level: int):
    sex_map = {
        0: "色気は出さない。",
        1: "ほんのり大人の余裕を感じさせる。",
        2: "自然な色気を上品に含める。",
        3: "大人の魅力をはっきりと表現する。"
    }
    return sex_map.get(level, sex_map[0])

# ==========================
# API1回のみ生成
# ==========================
def generate_all(profile, tone_level, sexy_level, long_mode, uploaded_image):

    tone_text = tone_level_to_text(tone_level)
    sexy_text = sexiness_to_text(sexy_level)

    intro_length = "600〜800文字" if long_mode else "300〜450文字"
    attack_length = "350〜500文字" if long_mode else "200〜300文字"

    prompt = f"""
あなたは以下の女性です。

【プロフィール】
{profile}

【雰囲気】
{tone_text}
{sexy_text}

①【画像分析】
画像があれば簡潔に分析。なければ「画像なし」と出力。

②【自己紹介】
{intro_length}で作成。自然な敬語。年齢を最初に明示。

③【アタック文章】
{attack_length}で作成。相手を1つ具体的に褒める。

④【AI人格プロンプト】
600文字以上。常に敬語。
"""

    config = GenerationConfig(
        temperature=0.65,
        top_p=0.85,
        max_output_tokens=600  # 無料枠安全域
    )

    contents = [prompt]

    if uploaded_image:
        image = Image.open(uploaded_image)
        image.thumbnail((512, 512))
        contents = [prompt, image]

    response = model.generate_content(
        contents,
        generation_config=config
    )

    return response.text.strip()

# ==========================
# Streamlit UI
# ==========================

st.title("AI生成ツール")

profile = st.text_area("プロフィール入力")

tone_level = st.slider("雰囲気", 1, 5, 3)
sexy_level = st.slider("色気", 0, 3, 1)
long_mode = st.checkbox("長文モード")

uploaded_image = st.file_uploader("画像アップロード", type=["jpg", "png"])

if "result" not in st.session_state:
    st.session_state.result = None

if st.button("生成する"):
    if profile.strip() == "":
        st.warning("プロフィールを入力してください。")
    else:
        st.session_state.result = generate_all(
            profile,
            tone_level,
            sexy_level,
            long_mode,
            uploaded_image
        )

if st.session_state.result:
    st.write(st.session_state.result)
