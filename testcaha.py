import google.generativeai as genai
from google.generativeai.types import GenerationConfig

# ==========================
# APIキー設定
# ==========================
genai.configure(api_key="YOUR_API_KEY")

model = genai.GenerativeModel("gemini-2.5-flash")

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
# 共通生成関数（InvalidArgument対策のみ修正）
# ==========================
def generate_text(prompt, max_tokens=1000):

    config = GenerationConfig(
        temperature=0.8,
        top_p=0.9,
        max_output_tokens=int(max_tokens)
    )

    response = model.generate_content(
        prompt,
        generation_config=config
    )

    return response.text.strip()

# ==========================
# 自己紹介生成
# ==========================
def generate_self_intro(profile, tone_level=3, sexy_level=0, long_mode=False):
    tone_text = tone_level_to_text(tone_level)
    sexy_text = sexiness_to_text(sexy_level)

    length_instruction = "600〜900文字で詳しく。" if long_mode else "300〜500文字で簡潔に。"

    prompt = f"""
あなたは以下の女性です。
{profile}

【雰囲気設定】
{tone_text}
{sexy_text}

【指示】
・{length_instruction}
・自然な敬語
・年齢を最初に明示
・趣味や休日を具体的に書く
・軽いエピソードを1つ入れる
・途中で絶対に終わらせない
・説明文は禁止
・完成した自己紹介文のみ出力

自己紹介を書いてください。
"""

    max_tokens = 1500 if long_mode else 800
    return generate_text(prompt, max_tokens)

# ==========================
# アタック文生成
# ==========================
def generate_attack(profile, tone_level=3, sexy_level=1, long_mode=False):
    tone_text = tone_level_to_text(tone_level)
    sexy_text = sexiness_to_text(sexy_level)

    length_instruction = "400〜600文字。" if long_mode else "200〜350文字。"

    prompt = f"""
あなたは以下の女性です。
{profile}

【雰囲気設定】
{tone_text}
{sexy_text}

【指示】
・{length_instruction}
・相手を具体的に1つ褒める
・趣味を自然に絡める
・軽すぎない
・大人の余裕
・途中終了禁止
・文章のみ出力

魅力的な初回メッセージを書いてください。
"""

    max_tokens = 1200 if long_mode else 600
    return generate_text(prompt, max_tokens)

# ==========================
# AI人格プロンプト生成
# ==========================
def generate_persona_prompt(profile, tone_level=3, sexy_level=0):
    tone_text = tone_level_to_text(tone_level)
    sexy_text = sexiness_to_text(sexy_level)

    prompt = f"""
以下の女性になりきって会話してください。
{profile}

【雰囲気設定】
{tone_text}
{sexy_text}

【人格ルール】
・常に敬語
・感情は自然に
・依存的にならない
・相手を否定しない
・恋愛は焦らない
・文章は読みやすく
・絵文字は適度に使用

800文字以上で詳細なAI人格プロンプトを出力してください。
"""

    return generate_text(prompt, 1500)

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

    tone_level = 4
    sexy_level = 2
    long_mode = True

    print("📝 自己紹介\n")
    print(generate_self_intro(profile, tone_level, sexy_level, long_mode))

    print("\n💌 アタック文\n")
    print(generate_attack(profile, tone_level, sexy_level, long_mode))

    print("\n🤖 AI人格プロンプト\n")
    print(generate_persona_prompt(profile, tone_level, sexy_level))
