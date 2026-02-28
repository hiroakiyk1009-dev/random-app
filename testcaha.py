import google.generativeai as genai
import os
import time

# ==========================
# APIキー設定
# ==========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 🔥 軽量安定モデルに変更（無料枠向き）
model = genai.GenerativeModel("gemini-1.5-flash")


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


# ==========================
# 色気レベル変換
# ==========================
def sexiness_to_text(level: int):
    sex_map = {
        0: "色気は出さない。",
        1: "ほんのり大人の余裕を感じさせる。",
        2: "自然な色気を上品に含める。",
        3: "大人の魅力をはっきりと表現する。"
    }
    return sex_map.get(level, sex_map[0])


# ==========================
# 共通生成関数（無料枠最適化版）
# ==========================
def generate_text(
    prompt,
    max_tokens=700,     # 🔥 大幅削減
    min_length=250,
    temperature=0.6,
    top_p=0.85
):
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "top_p": top_p,
                "max_output_tokens": max_tokens
            }
        )

        text = response.text.strip()

        # 🔥 文字数不足でも再生成しない（無料枠優先）
        if len(text) < min_length:
            text += "\n\n（※補足：文字数制限のため簡潔にまとめています。）"

        time.sleep(1.2)  # 🔥 レート制限対策

        return text

    except Exception as e:
        return f"⚠️ APIエラー: {e}"


# ==========================
# 自己紹介生成
# ==========================
def generate_self_intro(
    profile,
    tone_level=3,
    sexy_level=0,
    long_mode=False,
    temperature=0.6,
    top_p=0.85
):

    tone_text = tone_level_to_text(tone_level)
    sexy_text = sexiness_to_text(sexy_level)

    length_instruction = "500〜700文字" if long_mode else "300〜450文字"
    min_length = 450 if long_mode else 250
    max_tokens = 700 if long_mode else 500  # 🔥 削減

    prompt = f"""
あなたは以下の女性です。

【プロフィール】
{profile}

【雰囲気】
{tone_text}
{sexy_text}

【出力条件】
・{length_instruction}
・自然な敬語
・年齢を最初に明示
・趣味や休日を具体的に
・軽いエピソードを1つ
・自然な締めで終える

自己紹介文のみ出力。
"""

    return generate_text(prompt, max_tokens, min_length, temperature, top_p)


# ==========================
# アタック文生成
# ==========================
def generate_attack(
    profile,
    tone_level=3,
    sexy_level=1,
    long_mode=False,
    temperature=0.6,
    top_p=0.85
):

    tone_text = tone_level_to_text(tone_level)
    sexy_text = sexiness_to_text(sexy_level)

    length_instruction = "350〜500文字" if long_mode else "200〜300文字"
    min_length = 300 if long_mode else 200
    max_tokens = 600 if long_mode else 400  # 🔥 削減

    prompt = f"""
あなたは以下の女性です。

【プロフィール】
{profile}

【雰囲気】
{tone_text}
{sexy_text}

【出力条件】
・{length_instruction}
・相手を1つ具体的に褒める
・趣味を自然に絡める
・軽すぎない
・大人の余裕
・自然な締め

文章のみ出力。
"""

    return generate_text(prompt, max_tokens, min_length, temperature, top_p)


# ==========================
# AI人格プロンプト生成
# ==========================
def generate_persona_prompt(
    profile,
    tone_level=3,
    sexy_level=0,
    temperature=0.6,
    top_p=0.85
):

    tone_text = tone_level_to_text(tone_level)
    sexy_text = sexiness_to_text(sexy_level)

    prompt = f"""
以下の女性になりきるAI人格を作成する。

【プロフィール】
{profile}

【雰囲気】
{tone_text}
{sexy_text}

【人格ルール】
・常に敬語
・感情は自然に
・依存的にならない
・否定しない
・恋愛は焦らない
・読みやすい文章
・絵文字は適度

700文字以上で作成。
人格プロンプトのみ出力。
"""

    return generate_text(prompt, 800, 600, temperature, top_p)  # 🔥 削減


# ==========================
# 使用例
# ==========================
if __name__ == "__main__":

    profile = """
年齢：48歳（1978年10月17日生まれ）
職業：事務職または広報
趣味：カフェ巡り、読書、映画鑑賞、旅行
休日：友人とランチ、ショッピング、ドライブ
性格：穏やかで親しみやすい
顔文字：😉😊✨☕️💕
"""

    temperature = 0.65
    top_p = 0.88

    tone_level = 4
    sexy_level = 2
    long_mode = True

    print("📝 自己紹介\n")
    print(generate_self_intro(profile, tone_level, sexy_level, long_mode, temperature, top_p))

    print("\n💌 アタック文\n")
    print(generate_attack(profile, tone_level, sexy_level, long_mode, temperature, top_p))

    print("\n🤖 AI人格プロンプト\n")
    print(generate_persona_prompt(profile, tone_level, sexy_level, temperature, top_p))
