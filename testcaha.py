import streamlit as st
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from PIL import Image
import os

# ==========================
# APIキー設定
# ==========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.5-flash")

# ==========================
# 固定プロフィール（ここだけ編集）
# ==========================
PROFILE = """
年齢：48歳（1978年10月17日生まれ）
職業：事務職または広報
趣味：カフェ巡り、読書、映画鑑賞、旅行
休日：友人とランチ、ショッピング、ドライブ
性格：穏やかで親しみやすい
顔文字：😉😊✨☕️💕
"""

# ==========================
# 雰囲気レベル変換
# ==========================
def tone_level_to_text(level: int):
    return {
        1: "非常に落ち着き重視。感情表現は最小限。",
        2: "やや控えめ。上品で穏やか。",
        3: "自然で親しみやすい標準的な表現。",
        4: "感情豊かで柔らかい表現。",
        5: "かなり感情豊かで印象的。"
    }.get(level, "自然で親しみやすい標準的な表現。")

def sexiness_to_text(level: int):
    return {
        0: "色気は出さない。",
        1: "ほんのり大人の余裕を感じさせる。",
        2: "自然な色気を上品に含める。",
        3: "大人の魅力をはっきりと表現する。"
    }.get(level, "色気は出さない。")

# ==========================
# API 1回のみ実行関数
# ==========================
def generate_all(tone_level, sexy_level, image):

    tone_text = tone_level_to_text(tone_level)
    sexy_text = sexiness_to_text(sexy_level)

    prompt = f"""
あなたは以下の女性です。

【プロフィール】
{PROFILE}

【雰囲気】
{tone_text}
{sexy_text}

以下を順番通り出力してください。

①【画像の雰囲気分析】
画像があれば服装・表情・背景・印象を簡潔に。
なければ「画像なし」。

②【自己紹介文】
・300〜450文字
・自然な敬語
・年齢を最初に明示
・趣味や休日を具体的に
・軽いエピソード1つ

③【アタック文章】
・200〜300文字
・相手を具体的に1つ褒める
・趣味を絡める
・大人の余裕

④【AI人格プロンプト】
・常に敬語
・否定しない
・依存しない
・恋愛は焦らない
・600文字以上
"""

    config = GenerationConfig(
        temperature=0.65,
        top_p=0.85,
        max_output_tokens=600  # 無料枠安全値
    )

    contents = [prompt]

    if image:
        img = Image.open(image)
        img.thumbnail((512, 512))
        contents = [prompt, img]

    response = model.generate_content(
        contents,
        generation_config=config
    )

    return response.text


# ==========================
# Streamlit UI
# ==========================

st.title("プロフィール生成AI")

tone_level = st.slider("雰囲気レベル", 1, 5, 3)
sexy_level = st.slider("色気レベル", 0, 3, 1)

uploaded_image = st.file_uploader("画像アップロード（任意）", type=["jpg", "png"])

# 🔥 ボタン押したときだけAPI実行
if st.button("生成する"):
    with st.spinner("生成中..."):
        result = generate_all(
            tone_level,
            sexy_level,
            uploaded_image
        )
        st.write(result)
