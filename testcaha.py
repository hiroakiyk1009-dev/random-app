import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import time

# ==============================
# ページ設定
# ==============================
st.set_page_config(page_title="AIプロフィール生成", layout="centered")
st.title("✨ AIプロフィール自動生成")

# ==============================
# API設定
# ==============================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel(
    model_name="models/gemini-2.5-flash",
    generation_config={
        "temperature": 0.7,
        "top_p": 0.9,
        "max_output_tokens": 512,  # 無料枠対策
    },
)

# ==============================
# レート制御（簡易）
# ==============================
if "last_run" not in st.session_state:
    st.session_state.last_run = 0

def rate_limit():
    now = time.time()
    if now - st.session_state.last_run < 5:  # 5秒間隔
        st.warning("⚠ 少し待ってから再実行してください")
        return False
    st.session_state.last_run = now
    return True

# ==============================
# 画像解析
# ==============================
@st.cache_data(show_spinner=False)
def analyze_image(image):
    prompt = """
    この人物の雰囲気を分析してください。
    ・見た目の印象
    ・性格の予想
    ・モテタイプ分類
    100文字程度で簡潔に。
    """
    response = model.generate_content([prompt, image])
    return response.text

# ==============================
# テキスト生成
# ==============================
@st.cache_data(show_spinner=False)
def generate_text(prompt):
    response = model.generate_content(prompt)
    return response.text

# ==============================
# 入力UI
# ==============================
uploaded_file = st.file_uploader("画像をアップロード", type=["jpg", "jpeg", "png"])

weekend = st.selectbox("休日", ["週末", "平日休み", "不定休"])
marriage = st.selectbox("婚歴", ["独身", "バツなし", "バツあり"])
emoji_style = st.text_input("使いたい顔文字", "✨👌😘")

# ==============================
# 実行ボタン
# ==============================
if st.button("プロフィール生成"):
    if not rate_limit():
        st.stop()

    if uploaded_file is None:
        st.error("画像をアップしてください")
        st.stop()

    try:
        image = Image.open(uploaded_file)

        with st.spinner("画像解析中..."):
            analysis = analyze_image(image)

        profile_prompt = f"""
        以下の情報からマッチングアプリ用プロフィールを作成してください。

        【人物の雰囲気】
        {analysis}

        【休日】
        {weekend}

        【婚歴】
        {marriage}

        【使用顔文字】
        {emoji_style}

        300文字以内で、自然でモテる文章にしてください。
        """

        with st.spinner("プロフィール生成中..."):
            profile = generate_text(profile_prompt)

        st.subheader("📌 AIプロフィール")
        st.write(profile)

        with st.spinner("初対面アタック文生成中..."):
            attack = generate_text("初対面で使える軽めのアタック文を作成してください。\n" + profile)

        st.subheader("🔥 初対面アタック文")
        st.write(attack)

    except Exception as e:
        st.error("API制限に達した可能性があります。少し時間をおいて再試行してください。")
