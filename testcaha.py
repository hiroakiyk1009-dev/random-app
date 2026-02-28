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
# 全生成（API1回のみ）
# ==========================
def generate_all(profile, tone_level=3, sexy_level=0, long_mode=False, image_path=None):

    tone_text = tone_level_to_text(tone_level)
    sexy_text = sexiness_to_text(sexy_level)

    intro_length = "600〜800文字で詳しく。" if long_mode else "300〜450文字で簡潔に。"
    attack_length = "350〜500文字。" if long_mode else "200〜300文字。"

    prompt = f"""
あなたは以下の女性です。

【プロフィール】
{profile}

【雰囲気】
{tone_text}
{sexy_text}

以下を必ず順番通り出力してください。

①【画像の雰囲気分析】
画像がある場合は服装・表情・背景・全体印象を簡潔に分析。
画像がない場合は「画像なし」と明記。

②【自己紹介文】
・{intro_length}
・自然な敬語
・年齢を最初に明示
・趣味や休日を具体的に
・軽いエピソードを1つ入れる
・途中終了禁止
・完成文のみ出力

③【アタック文章】
・{attack_length}
・相手を具体的に1つ褒める
・趣味を自然に絡める
・軽すぎない
・大人の余裕
・途中終了禁止
・完成文のみ出力

④【AI人格プロンプト】
・常に敬語
・感情は自然に
・依存しない
・否定しない
・恋愛は焦らない
・読みやすく
・絵文字は適度
・600文字以上
"""

    # 🔒 無料枠対策
    config = GenerationConfig(
        temperature=0.65,
        top_p=0.85,
        max_output_tokens=650   # ← ここ重要（安全値）
    )

    contents = [prompt]

    if image_path and os.path.exists(image_path):
        image = Image.open(image_path)
        image.thumbnail((512, 512))  # トークン削減
        contents = [prompt, image]

    response = model.generate_content(
        contents,
        generation_config=config
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
    image_path = None  # 例: "sample.jpg"

    result = generate_all(
        profile,
        tone_level,
        sexy_level,
        long_mode,
        image_path
    )

    print(result)
