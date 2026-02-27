import google.generativeai as genai

# ==========================
# APIキー設定
# ==========================
genai.configure(api_key="YOUR_API_KEY")

# 軽量＆安定モデル
model = genai.GenerativeModel("models/gemini-2.5-flash")

# ==========================
# 雰囲気変換（簡略版）
# ==========================
def tone_text(level):
    return [
        "落ち着き重視",
        "やや控えめ",
        "自然で親しみやすい",
        "感情豊か",
        "印象的で華やか"
    ][level-1] if 1 <= level <= 5 else "自然"

def sexy_text(level):
    return [
        "色気なし",
        "ほんのり大人",
        "上品な色気",
        "大人の魅力強め"
    ][level] if 0 <= level <= 3 else "色気なし"

# ==========================
# 共通生成（超軽量設定）
# ==========================
def generate_text(prompt, max_tokens=600):
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,      # 安定
                "top_p": 0.85,           # 暴走防止
                "max_output_tokens": max_tokens
            }
        )
        return response.text.strip()
    except Exception as e:
        return f"生成エラー: {e}"

# ==========================
# 自己紹介（軽量）
# ==========================
def generate_self_intro(profile, tone=3, sexy=0, long_mode=False):

    length = "600字以内" if long_mode else "350字以内"

    prompt = f"""
あなたは以下の女性です。

{profile}

雰囲気:{tone_text(tone)}
色気:{sexy_text(sexy)}

条件:
・{length}
・敬語
・年齢を最初に書く
・趣味を自然に入れる
・最後まで必ず書き切る
・説明文禁止

自己紹介のみ出力
"""

    return generate_text(prompt, 900 if long_mode else 500)

# ==========================
# アタック文（軽量）
# ==========================
def generate_attack(profile, tone=3, sexy=1, long_mode=False):

    length = "500字以内" if long_mode else "250字以内"

    prompt = f"""
あなたは以下の女性です。

{profile}

雰囲気:{tone_text(tone)}
色気:{sexy_text(sexy)}

条件:
・{length}
・敬語
・相手を1つ褒める
・大人の余裕
・途中終了禁止
・文章のみ

魅力的な初回メッセージを書いてください
"""

    return generate_text(prompt, 800 if long_mode else 400)

# ==========================
# AI人格プロンプト（軽量）
# ==========================
def generate_persona_prompt(profile, tone=3, sexy=0):

    prompt = f"""
以下の女性になりきって会話するAI設定を書いてください。

{profile}

雰囲気:{tone_text(tone)}
色気:{sexy_text(sexy)}

条件:
・敬語
・自然な感情表現
・否定しない
・依存しない
・読みやすい
・800字以内

AI人格プロンプトのみ出力
"""

    return generate_text(prompt, 900)

# ==========================
# 使用例
# ==========================
if __name__ == "__main__":

    profile = """
年齢：48歳
職業：事務職または広報
趣味：カフェ巡り、読書、映画鑑賞、旅行
休日：友人とランチ、ショッピング、ドライブ
性格：穏やかで親しみやすい
顔文字：😉😊✨☕️💕
"""

    print("📝 自己紹介\n")
    print(generate_self_intro(profile, 4, 2, False))

    print("\n💌 アタック文\n")
    print(generate_attack(profile, 4, 2, False))

    print("\n🤖 AI人格プロンプト\n")
    print(generate_persona_prompt(profile, 4, 2))
