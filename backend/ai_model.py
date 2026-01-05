# backend/ai_model.py（修正版・完全版）

import json
import os
import re
from typing import Any
import logging
from inference_manager import get_inference_manager

logger = logging.getLogger(__name__)

# =========================
# 設定（環境変数で上書き可）
# =========================
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "60"))

# =========================
# 正規化関数
# =========================
def normalize_minus_words(words: Any, max_len: int = 50, max_items: int = 10) -> list[str]:
    """
    minus_words の正規化
    - list以外は空配列
    - 各要素を str 化・strip
    - 空文字を除外
    - 長すぎるフレーズをカット
    - 重複除去（順序保持）
    
    Args:
        words: 正規化対象のワードリスト
        max_len: 1フレーズの最大文字数
        max_items: 最大アイテム数
    
    Returns:
        list[str]: 正規化されたワードリスト
    """
    if not isinstance(words, list):
        return []

    normalized: list[str] = []
    seen = set()

    for w in words:
        if w is None:
            continue
        s = str(w).strip()
        if not s:
            continue

        # 長すぎるフレーズをカット
        if len(s) > max_len:
            s = s[:max_len] + "…"

        # 重複除去
        if s in seen:
            continue

        seen.add(s)
        normalized.append(s)

        # 最大数制限
        if len(normalized) >= max_items:
            break

    return normalized


# =========================
# AI応答生成関数（メイン）
# =========================
async def generate_ai_response(prompt: str, temperature: float = 0.7, max_tokens: int = 512) -> str:
    """
    AI応答を生成（シンプル版：テキストのみ返却）
    
    Args:
        prompt (str): プロンプト
        temperature (float): 温度パラメータ（0.0-1.0）
        max_tokens (int): 最大トークン数
    
    Returns:
        str: 生成されたテキスト
    
    Raises:
        TimeoutError: 推論がタイムアウトした場合
        Exception: その他のエラー
    """
    logger.debug(f"AI応答生成開始: {prompt[:50]}...")
    
    try:
        # 推論マネージャーを取得
        inference_manager = get_inference_manager()
        
        # 推論実行
        result = await inference_manager.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=int(REQUEST_TIMEOUT)
        )
        
        logger.info(f"✅ AI応答生成成功 (長さ: {len(result)}文字)")
        return result
    
    except TimeoutError as e:
        logger.error("⏱️ AI応答生成タイムアウト")
        raise
    
    except Exception as e:
        logger.error(f"❌ AI応答生成エラー: {e}")
        raise


# =========================
# マイナスワード検出＋アドバイス生成
# =========================
async def generate_advice(inputed_text: str) -> dict[str, Any]:
    """
    llama.cpp を使ってマイナスワード検出とアドバイスを生成

    Args:
        inputed_text: ユーザーの入力文章

    Returns:
        dict: {"minus_words": ["ダメ", "無理"], "advice": "大丈夫です！"}
    """
    
    logger.info(f"マイナスワード検出開始: {inputed_text[:50]}...")

    # ===== セキュリティ対策: プロンプトインジェクション防止 =====
    safe_input_text = inputed_text.replace("<start_of_turn>", "").replace("<end_of_turn>", "")
    # 極端に長い入力の制限
    if len(safe_input_text) > 500:
        safe_input_text = safe_input_text[:500]
        logger.warning(f"⚠️ 入力文が500文字を超えたためトリミングしました")

    system_prompt = """あなたは「マイナスワード検出アシスタント」です。

# マイナスワードの定義
相手の自尊心ややる気を下げる可能性のあるグレーな表現を検出してください。

## 検出対象(5カテゴリ)
1. 否定の決めつけ: 「どうせ無理」「私なんて」
2. 比較による圧力: 「みんなはできるのに」「普通は〜」
3. 皮肉・嫌味: 「へー、すごいね」「さすがですね」
4. 強制・圧力: 「〜すべき」「〜しなければ」
5. 過去の否定: 「前もダメだった」「いつも失敗」

※ 露骨な罵倒語（バカ、死ね等）も検出対象に含めます。

## 抽出ルール
- フレーズ単位で抽出(意味のある塊)
- 同じ意味の言い換えは1つにまとめる
- 重複は除く
- 最大10個まで

# 出力形式
{
  "minus_words": ["抽出された表現1", "抽出された表現2"],
  "advice": "120文字以内のマイナスワードに対しての言動の改善アドバイス"
}

# アドバイスの作成ルール
- まず相手の辛い気持ちに共感する
- 責めたり診断したりしない
- 「〜しましょう」より「〜してみませんか？」という提案形
- 具体的な行動提案を含める
- 罵倒語が含まれる場合は、優しく諭すトーンで

# 重要
- JSON以外は出力しない
- マイナスワードなし → minus_words は []
- 必ず日本語で応答

# 例

## 例1: 複数パターン
入力: "みんなはできるのに、私だけできない。前回も失敗した。"
出力:
{
  "minus_words": ["みんなはできるのに、私だけできない", "前回も失敗した"],
  "advice": "周りと比べて焦る気持ち、よく分かります。前回の経験は次に活きますよ。まずは今日できた小さなことを1つ振り返ってみませんか？あなたのペースで大丈夫です。"
}

## 例2: マイナスワードなし
入力: "今日はいい天気ですね。"
出力:
{
  "minus_words": [],
  "advice": "前向きな気持ちが伝わってきます。その調子で自分のペースを大切にしてくださいね。"
}
"""

    user_prompt = f"""次の文章を解析し、マイナスワードを抽出してJSON形式で返してください。

入力文:
{safe_input_text}

JSON形式で返してください。"""

    # Gemma2用のプロンプト形式
    prompt = f"""<start_of_turn>system
{system_prompt}<end_of_turn>
<start_of_turn>user
{user_prompt}<end_of_turn>
<start_of_turn>model
"""

    try:
        # ===== 推論マネージャーで生成実行 =====
        inference_manager = get_inference_manager()
        
        result = await inference_manager.generate(
            prompt=prompt,
            max_tokens=300,  # バランス型: 日本語120文字+JSON構造+余裕
            temperature=0.7,
            top_p=0.9,
            timeout=int(REQUEST_TIMEOUT)
        )

        if not result:
            logger.warning("⚠️ 空の応答が返されました")
            return {
                "minus_words": [],
                "advice": "申し訳ありません、うまく解析できませんでした。別の表現でもう一度試してみてください。"
            }

        logger.debug(f"生成結果（raw）: {result[:200]}...")

        # ===== JSON抽出ロジック(強化版) =====
        # 1. { } で囲まれた部分を抽出
        json_start = result.find('{')
        json_end = result.rfind('}') + 1

        if json_start != -1 and json_end > json_start:
            json_str = result[json_start:json_end]
        else:
            # フォールバック: Markdownクリーニング
            json_str = re.sub(r'```json\n?', '', result)
            json_str = re.sub(r'```\n?', '', json_str)
            json_str = json_str.strip()

        logger.debug(f"抽出されたJSON文字列: {json_str[:200]}...")

        # ===== JSON検証とパース =====
        try:
            parsed = json.loads(json_str)

            # advice の型と長さを検証
            if not isinstance(parsed.get("advice"), str):
                logger.warning("⚠️ adviceが文字列ではありません。デフォルト値を設定します。")
                parsed["advice"] = "申し訳ありません、うまく解析できませんでした。別の表現でもう一度試してみてください。"

            # 文字数制限チェック(余裕を持たせる)
            if len(parsed["advice"]) > 130:
                logger.warning(f"⚠️ adviceが長すぎます（{len(parsed['advice'])}文字）。トリミングします。")
                parsed["advice"] = parsed["advice"][:127] + "..."

            # minus_words を正規化（★重要）
            parsed["minus_words"] = normalize_minus_words(parsed.get("minus_words"))

            logger.info(f"✅ マイナスワード検出完了: {len(parsed['minus_words'])}個")
            return parsed

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"❌ JSON parse error: {e}, Raw result: {result}")
            # JSONパース失敗時のフォールバック
            return {
                "minus_words": [],
                "advice": "申し訳ありません、うまく解析できませんでした。別の表現でもう一度試してみてください。"
            }

    except TimeoutError:
        logger.error("⏱️ マイナスワード検出タイムアウト")
        return {
            "minus_words": [],
            "advice": "申し訳ありません、処理に時間がかかりすぎました。少し時間を置いてもう一度お試しください。"
        }

    except Exception as e:
        logger.error(f"❌ generate_advice error: {e}")
        import traceback
        traceback.print_exc()
        # システムエラー時
        return {
            "minus_words": [],
            "advice": "申し訳ありません、一時的なエラーが発生しました。少し時間を置いてもう一度お試しください。"
        }
