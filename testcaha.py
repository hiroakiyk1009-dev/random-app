import google.generativeai as genai
from PIL import Image

# ==========================
# APIキー設定
# ==========================
genai.configure(api_key="YOUR_API_KEY")

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
# API 1回のみ統合生成（画像含む）
# ==========================
def generate_all(profile,
                 tone_level=3,
                 sexy_level=0,
                 long_mode=False,
                 image_path=None):

    tone_text = tone_level_to_text(tone_level)
    sexy_text = sexiness_to_text(sexy_level)

    self_length = "600〜900文字で詳しく。" if long_mode else "300〜500文字で簡潔に。"
    attack_length = "400〜600文字。" if long_mode else "200〜350文字。"

    prompt = f"""
あなたは以下の女性です。

{profile}

【雰囲気設定】
{tone_text}
{sexy_text}

====================
【① 画像雰囲気判定】
・落ち着き度（1〜5）
・色気度（0〜3）
・第一印象を一言
※画像が無い場合は「画像なし」と出力

====================
【② 自己紹介】
・{self_length}
・自然な敬語
・年齢を最初に明示
・趣味や休日を具体的に
・軽いエピソードを1つ
・自然に締める

====================
【③ アタック文】
・{attack_length}
・相手を具体的に1つ褒める
・趣味を絡める
・大人の余裕
・自然に締める

====================
【④ AI人格プロンプト】
・800文字以上
・常に敬語
・依存しない
・相手を否定しない
・恋愛は焦らない
・読みやすく

必ず4つすべて出力すること。
各セクションにタイトルをつけること。
"""

    # 画像がある場合はマルチモーダル入力
    if image_path:
        image = Image.open(image_path)
        response = model.generate_content(
            [prompt, image],
            generation_config={
                "temperature": 0.65,
                "top_p": 0.85,
                "max_output_tokens": 1600
            }
        )
    else:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.65,
                "top_p": 0.85,
                "max_output_tokens": 1600
            }
        )

    return response.text.strip()

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

    # 画像パス（なければ None）
    image_path = None
    # image_path = "sample.jpg"

    result = generate_all(
        profile,
        tone_level,
        sexy_level,
        long_mode,
        image_path
    )

    print(result)
