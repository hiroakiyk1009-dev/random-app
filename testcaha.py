import streamlit as st
import google.generativeai as genai
import os
import time
import hashlib

# ==========================
# APIキー設定
# ==========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")  # 2.5より安定＆軽量

# ==========================
# キャッシュ用キー生成
# ==========================
def make_cache_key(*args):
    raw = "|".join(map(str, args))
    return hashlib.md5(raw.encode()).hexdigest()

# ==========================
# 共通生成関数（無料枠最適化版）
# ==========================
def generate_text(prompt, max_tokens=700, temperature=0.6, top_p=0.85):

    time.sleep(1.2)  # レート制限対策

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "top_p": top_p,
                "max_output_tokens": max_tokens
            }
        )
        return response.text.strip()

    except Exception as e:
        return f"⚠ エラーが発生しました: {e}"

# ==========================
# UI
# ==========================
st.title("💎 AIプロフィール生成（最適化版）")

profile = st.text_area("プロフィールを入力", height=200)

tone_level = st.slider("雰囲気レベル", 1, 5, 3)
sexy_level = st.slider("色気レベル", 0, 3, 1)
long_mode = st.checkbox("長文モード")

temperature = st.slider("Temperature", 0.2, 1.0, 0.6)
top_p = st.slider("Top P", 0.5, 1.0, 0.85)

# ==========================
# セッション管理
# ==========================
if "last_key" not in st.session_state:
    st.session_state.last_key = None
if "result" not in st.session_state:
    st.session_state.result = None

# ==========================
# 生成ボタン
# ==========================
if st.button("✨ 生成する"):

    if not profile.strip():
        st.warning("プロフィールを入力してください")
    else:

        cache_key = make_cache_key(
            profile, tone_level, sexy_level,
            long_mode, temperature, top_p
        )

        # 同じ条件ならAPIを呼ばない
        if cache_key == st.session_state.last_key:
            st.info("同じ条件のため再生成していません")
        else:

            length_instruction = "600〜900文字" if long_mode else "300〜500文字"
            max_tokens = 900 if long_mode else 600

            prompt = f"""
あなたは以下の女性です。

【プロフィール】
{profile}

【雰囲気】
雰囲気レベル:{tone_level}
色気レベル:{sexy_level}

【条件】
・{length_instruction}
・自然な敬語
・必ず自然な締めで終える
・文章のみ出力
"""

            result = generate_text(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )

            st.session_state.result = result
            st.session_state.last_key = cache_key

# ==========================
# 結果表示
# ==========================
if st.session_state.result:
    st.markdown("### 📝 生成結果")
    st.write(st.session_state.result)
