# backend/inference_manager.py（新規・完全版）

import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import traceback
import logging
import psutil
from llama_cpp import Llama
from config import MODEL_PATH

logger = logging.getLogger(__name__)

def get_optimal_threads():
    """
    最適なスレッド数を計算
    
    Returns:
        int: 推論に使用するスレッド数
    """
    try:
        physical_cores = psutil.cpu_count(logical=False)
        if physical_cores is None:
            physical_cores = 2  # フォールバック
        
        # 物理コアの80%を使用（他プロセスのため余裕を持たせる）
        optimal_threads = max(1, int(physical_cores * 0.8))
        
        logger.info(f"💻 CPU情報: 物理コア={physical_cores}, 推論スレッド={optimal_threads}")
        return optimal_threads
    except Exception as e:
        logger.warning(f"⚠️ CPU情報取得失敗: {e}. デフォルト値(2)を使用")
        return 2

def get_optimal_batch_size():
    """
    メモリに応じた最適バッチサイズ
    
    Returns:
        int: バッチサイズ
    """
    try:
        available_memory_gb = psutil.virtual_memory().available / (1024**3)
        
        if available_memory_gb > 8:
            batch_size = 512
        elif available_memory_gb > 4:
            batch_size = 256
        else:
            batch_size = 128
        
        logger.info(f"💾 メモリ: 利用可能={available_memory_gb:.1f}GB, バッチサイズ={batch_size}")
        return batch_size
    except Exception as e:
        logger.warning(f"⚠️ メモリ情報取得失敗: {e}. デフォルト値(256)を使用")
        return 256

class InferenceManager:
    """推論エンジンの管理・隔離・再初期化"""
    
    def __init__(self, model_path: str, max_workers: int = 1):
        """
        InferenceManagerを初期化
        
        Args:
            model_path (str): モデルファイルのパス
            max_workers (int): ワーカー数（デフォルト: 1）
        """
        self.model_path = model_path
        self.llm = None
        self.lock = Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.error_count = 0
        self.max_errors = 3  # 3回連続エラーで再初期化
        
        self._initialize()
    
    def _initialize(self):
        """モデルを初期化"""
        try:
            logger.info("🔄 モデルを読み込み中...")
            logger.info(f"📂 モデルパス: {self.model_path}")
            
            if not self.model_path:
                raise ValueError("モデルパスが設定されていません")
            
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=2048,                      # コンテキストサイズ
                n_threads=get_optimal_threads(), # スレッド数（自動最適化）
                n_batch=get_optimal_batch_size(), # バッチサイズ（自動最適化）
                use_mlock=True,                  # メモリロック（スワップ防止）
                verbose=False                     # 詳細ログを抑制
            )
            
            self.error_count = 0
            logger.info("✅ モデル読み込み完了")
            
        except Exception as e:
            logger.error(f"❌ モデル読み込み失敗: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def _reinitialize(self):
        """モデルを再初期化"""
        logger.warning("⚠️ モデルを再初期化します...")
        
        try:
            # 古いインスタンスを破棄
            if self.llm is not None:
                del self.llm
                self.llm = None
            
            # 再初期化
            self._initialize()
            logger.info("✅ 再初期化成功")
            
        except Exception as e:
            logger.error(f"❌ 再初期化失敗: {e}")
            raise
    
    def _inference_worker(self, prompt: str, **kwargs):
        """
        推論を実行（別スレッド）
        
        Args:
            prompt (str): プロンプト
            **kwargs: 推論パラメータ
        
        Returns:
            str: 生成されたテキスト
        
        Raises:
            RuntimeError: モデルが初期化されていない場合
            Exception: 推論エラー
        """
        try:
            with self.lock:  # 同時実行を防ぐ
                if self.llm is None:
                    raise RuntimeError("モデルが初期化されていません")
                
                logger.debug(f"🤖 推論開始: {prompt[:50]}...")
                
                output = self.llm(
                    prompt=prompt,
                    max_tokens=kwargs.get('max_tokens', 512),
                    temperature=kwargs.get('temperature', 0.7),
                    top_p=kwargs.get('top_p', 0.9),
                    stop=["</s>", "\n\n"],
                    echo=False
                )
                
                # 成功したらエラーカウントをリセット
                self.error_count = 0
                
                result = output["choices"][0]["text"].strip()
                logger.debug(f"✅ 推論完了: {len(result)}文字")
                
                return result
        
        except Exception as e:
            self.error_count += 1
            logger.error(f"⚠️ 推論エラー ({self.error_count}/{self.max_errors}): {e}")
            
            # 連続エラーが閾値を超えたら再初期化
            if self.error_count >= self.max_errors:
                logger.warning("🔄 エラー回数が閾値を超えました。再初期化します。")
                try:
                    self._reinitialize()
                except Exception as reinit_error:
                    logger.error(f"❌ 再初期化も失敗しました: {reinit_error}")
            
            raise
    
    async def generate(self, prompt: str, timeout: int = 60, **kwargs):
        """
        非同期で推論を実行（タイムアウト付き）
        
        Args:
            prompt (str): プロンプト
            timeout (int): タイムアウト秒数
            **kwargs: 推論パラメータ
        
        Returns:
            str: 生成されたテキスト
        
        Raises:
            TimeoutError: タイムアウトした場合
            Exception: その他のエラー
        """
        loop = asyncio.get_event_loop()
        
        try:
            # 別スレッドで推論を実行
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    self.executor,
                    self._inference_worker,
                    prompt,
                    kwargs
                ),
                timeout=timeout
            )
            return result
        
        except asyncio.TimeoutError:
            logger.error(f"⏱️ タイムアウト ({timeout}秒)")
            raise TimeoutError(f"推論が{timeout}秒でタイムアウトしました")
        
        except Exception as e:
            logger.error(f"❌ 推論失敗: {e}")
            raise
    
    def shutdown(self):
        """シャットダウン"""
        logger.info("🛑 推論エンジンをシャットダウン中...")
        
        self.executor.shutdown(wait=True)
        
        if self.llm is not None:
            del self.llm
            self.llm = None
        
        logger.info("✅ 推論エンジンシャットダウン完了")

# グローバルインスタンス
inference_manager = None

def get_inference_manager():
    """
    InferenceManagerのシングルトン取得
    
    Returns:
        InferenceManager: 推論マネージャーインスタンス
    
    Raises:
        Exception: 初期化失敗時
    """
    global inference_manager
    
    if inference_manager is None:
        logger.info("🔧 推論マネージャーを初期化中...")
        
        if MODEL_PATH is None:
            raise ValueError("モデルパスが設定されていません。config.pyを確認してください。")
        
        inference_manager = InferenceManager(model_path=MODEL_PATH)
    
    return inference_manager
