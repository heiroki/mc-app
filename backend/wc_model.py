import io
import os
import re
from collections import Counter

from janome.tokenizer import Tokenizer
from wordcloud import WordCloud


class WordCloudGenerator:
    def __init__(self):
        self.tokenizer = Tokenizer()

        # ===== ストップワード(ワードクラウド用・約60語) =====
        # マイナスワード検出とは異なり、視覚化用の除外語
        self.stop_words = {
            # 助詞(文法接続のみ)
            'の', 'は', 'が', 'を', 'に', 'と', 'で', 'や', 'も',
            'から', 'まで', 'より', 'へ', 'ば', 'て', 'つ',

            # 複合助詞
            'において', 'における', 'について', 'にて',
            'によって', 'により', 'による',

            # 丁寧語
            'です', 'ます', 'ました',
            'おり', 'おります', 'あり', 'あります',
            'い', 'いる', 'います',

            # 一人称
            '私', 'わたし', '僕', '俺',

            # 場所指示語
            'ここ', 'そこ', 'あそこ', 'どこ',

            # 抽象形式名詞
            'こと', 'もの', 'ため', 'ところ', 'うち',

            # その他(元のリストから必要なもの)
            'それ', 'よう', 'これ', 'そう', 'あなた', 'あれ', 'いつ',
            'とき', 'なに', 'なん', 'よ', 'ん', 'だ', 'た', 'な', 'く',
            're', # 元のリストにあった'れる'の一部
        }

        # ===== 品詞ベースの除外設定 =====
        self.exclude_pos = {
            '助詞',
            '記号',
            '空白',
            '補助記号',
        }

    def extract_words_from_minus_words(self, minus_words: list[str]) -> list[str]:
        """
        マイナスワード（文章）から名詞・形容詞・動詞を抽出
        例: 「誰も私を理解してくれない」→ ['誰', '理解', 'くれ', 'ない']
        改善点:
        - 品詞ベースの除外を追加
        - 否定語・感情語を保持
        - ストップワードの安全性を向上
        """
        words = []

        for text in minus_words:
            # 絵文字・一部記号を除去(ただし「!」「?」は残す)
            text = re.sub(r'[^\w\s!?ー〜]', '', text)

            for token in self.tokenizer.tokenize(text):
                parts = token.part_of_speech.split(',')
                word_type = parts[0]
                word_subtype = parts[1] if len(parts) > 1 else ''
                surface = token.surface

                # ===== 1. 品詞ベースで除外 =====
                if word_type in self.exclude_pos:
                    continue

                # ===== 2. ストップワード除外(最小限) =====
                if surface in self.stop_words:
                    continue

                # ===== 3. 名詞・形容詞・動詞を抽出 =====
                # 名詞の場合
                if word_type == '名詞':
                    # 一般名詞・固有名詞・形容動詞語幹を保持
                    if word_subtype in ['一般', '固有名詞', '形容動詞語幹']:
                        if len(surface) > 1:  # 1文字除外
                            words.append(surface)
                    # ⚠️ 非自立名詞は除外(「こと」「もの」など)
                    elif word_subtype == '非自立':
                        continue

                # 形容詞の場合(感情語として重要)
                elif word_type == '形容詞':
                    if len(surface) > 1:
                        words.append(surface)

                # 動詞の場合(基本形に変換)
                elif word_type == '動詞':
                    # 基本形(原形)を取得
                    base_form = parts[6] if len(parts) > 6 and parts[6] != '*' else surface
                    if len(base_form) > 1:
                        words.append(base_form)

                # ===== 4. 副詞・連体詞も保持(感情表現で重要) =====
                elif word_type in ['副詞', '連体詞']:
                    # 否定的な副詞を保持
                    negative_adverbs = ['どうせ', 'やっぱり', 'また', 'いつも', 'もう', 'そんな', 'あんな']
                    if surface in negative_adverbs or len(surface) > 2:
                        words.append(surface)

        print(f"[DEBUG] Extracted words: {words}")  # デバッグ用
        return words

    def _get_font_path(self) -> str | None:
        """OSに応じた日本語フォントパスを取得"""
        # Windowsのフォントパス（優先順位順）
        windows_fonts = [
            'C:\\Windows\\Fonts\\msgothic.ttc',
            'C:\\Windows\\Fonts\\meiryo.ttc',
            'C:\\Windows\\Fonts\\YuGothM.ttc',
            'C:\\Windows\\Fonts\\YuGothB.ttc',
        ]

        # Macのフォントパス
        mac_fonts = [
            '/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc',
            '/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc',
            '/System/Library/Fonts/Hiragino Sans GB.ttc',
        ]

        # Linuxのフォントパス
        linux_fonts = [
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf',
        ]

        all_fonts = windows_fonts + mac_fonts + linux_fonts

        for font_path in all_fonts:
            if os.path.exists(font_path):
                print(f"使用するフォント: {font_path}")
                return font_path

        print("警告: 日本語フォントが見つかりません。デフォルトフォントを使用します")
        return None

    def generate_wordcloud_image(
        self,
        words: list[str],
        width: int = 800,
        height: int = 400,
        background_color: str = 'white',
        colormap: str = 'Reds'
    ) -> io.BytesIO:
        """ワードクラウド画像を生成"""

        if not words:
            # 単語がない場合は空の画像を返す
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            text = "データがありません"
            font_path = self._get_font_path()
            try:
                if font_path:
                    font = ImageFont.truetype(font_path, 40)
                else:
                    font = ImageFont.load_default()
            except OSError:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            position = ((width - text_width) // 2, (height - text_height) // 2)
            draw.text(position, text, fill='gray', font=font)

            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            return img_io

        # マイナスワードから単語を抽出
        extracted_words = self.extract_words_from_minus_words(words)

        if not extracted_words:
            # 単語が抽出できなかった場合
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            text = "キーワードが抽出できませんでした"
            font_path = self._get_font_path()
            try:
                if font_path:
                    font = ImageFont.truetype(font_path, 30)
                else:
                    font = ImageFont.load_default()
            except OSError:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            position = ((width - text_width) // 2, (height - text_height) // 2)
            draw.text(position, text, fill='gray', font=font)

            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            return img_io

        # 単語の出現頻度をカウント
        word_freq = Counter(extracted_words)

        print(f"[DEBUG] Word frequencies: {word_freq}")

        # フォントパス取得
        font_path = self._get_font_path()

        # ワードクラウド生成
        wc = WordCloud(
            font_path=font_path,
            width=width,
            height=height,
            background_color=background_color,
            colormap=colormap,
            max_words=100,
            relative_scaling=0.5,
            min_font_size=10,
            max_font_size=100,
            prefer_horizontal=0.7,
            random_state=42
        ).generate_from_frequencies(word_freq)

        # 画像をバイナリに変換
        img_io = io.BytesIO()
        wc.to_image().save(img_io, 'PNG')
        img_io.seek(0)

        return img_io
