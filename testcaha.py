import streamlit as st
import google.generativeai as genai
from datetime import datetime
import random
from PIL import Image
import io

# ==========================
# APIキー設定
# ==========================
def configure_api():
    genai.configure(api_key="YOUR_API_KEY")
    return genai.GenerativeModel("gemini-1.5-pro-vision-latest")

# ==========================
# キャラメモ生成
# ==========================
def generate_character_memo(model, image_bytes, mime_type, age):
    birth_year = datetime.now().year - age
    birth_date = f"{birth_year}年{random.randint(1,12):02d}月{random.randint(1,28):02d}日"
    blood_types = ["A型", "B型", "O型", "AB型"]
    blood_type = random.choice(blood_types)

    prompt = f"""
以下の女性の画像をもとに、キャラメモを作成してください。

【条件】
・口調：敬語
・出力形式：以下の例に厳密に従うこと
・本名：画像から自然に推定して日本人女性の名前を生成してください（ふりがな付き）
・年齢：{age}歳（{birth_date}生まれ、{blood_type}）
・職業：画像から推定
・顔文字：画像から推定
・趣味：画像から推定（2つ以上）
・車：画像から推定
・写メ：出力しない

【出力例】
キャラメモ：

改行：1行　
口調：敬語　
本名：宮崎 歩実（みやざき　あゆみ）　
年齢：38歳（1972年05月09日生まれ、O型）　
職業：受付　
休日：週末　
婚歴：独身　
顔文字：✨👌😘　
趣味：サイクリング、ジョギング　
車：レクサス nx　
写メ⇒

【画像の内容をもとに、上記の形式でキャラメモを出力してください】
"""

    image = Image.open(io.BytesIO(image_bytes))

    response = model.generate_content(
        [prompt, image],
        generation_config={
            "temperature": 0.7,
            "top_p": 0.9,
            "max_output_tokens": 1000
        }
    )
    return response.text.strip()

# ==========================
# Streamlit UI
# ==========================
def main():
    st.title("📸 キャラメモ生成ツール")

    age = st.slider("年齢を選んでください", 20, 70, 30)
    uploaded_file = st.file_uploader("女性の画像をアップロードしてください", type=["jpg", "jpeg", "png"])

    if st.button("キャラメモを生成"):
        if uploaded_file:
            with st.spinner("画像を解析中... 🍄"):
                model = configure_api()
                image_bytes = uploaded_file.read()
                mime_type = uploaded_file.type
                result = generate_character_memo(model, image_bytes, mime_type, age)
                st.success("✅ キャラメモ生成完了！")
                st.text_area("📝 キャラメモ", result, height=400)
        else:
            st.warning("画像をアップロードしてください。")

if __name__ == "__main__":
    main()
