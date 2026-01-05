# build/download_model.py（修正版）

import os
import sys
from pathlib import Path

def download_model():
    """Hugging Faceからモデルをダウンロード"""
    
    # 環境変数から設定を取得（GitHub Actions用）
    model_repo = os.getenv('MODEL_REPO', 'mmnga/gemma-2-2b-jpn-it-gguf')
    model_name = os.getenv('MODEL_NAME', 'gemma-2-2b-jpn-it-Q4_K_M.gguf')
    
    # プロジェクトルート
    project_root = Path(__file__).parent.parent
    models_dir = project_root / 'models'
    models_dir.mkdir(exist_ok=True)
    
    model_path = models_dir / model_name
    
    # 既にダウンロード済みか確認
    if model_path.exists():
        size_gb = model_path.stat().st_size / (1024**3)
        print(f"[OK] Model already exists: {model_path} ({size_gb:.2f} GB)")
        return
    
    print("=" * 60)
    print("[INFO] Downloading model from Hugging Face...")
    print(f"   Repository: {model_repo}")
    print(f"   File: {model_name}")
    print(f"   Destination: {model_path}")
    print("=" * 60)
    
    try:
        # huggingface_hubをインポート
        from huggingface_hub import hf_hub_download
        
        # モデルをダウンロード
        downloaded_path = hf_hub_download(
            repo_id=model_repo,
            filename=model_name,
            local_dir=str(models_dir),
            local_dir_use_symlinks=False,
            resume_download=True,  # 中断された場合は再開
        )
        
        size_gb = Path(downloaded_path).stat().st_size / (1024**3)
        print("=" * 60)
        print("[OK] Model downloaded successfully!")
        print(f"   Size: {size_gb:.2f} GB")
        print(f"   Path: {downloaded_path}")
        print("=" * 60)
        
    except ImportError:
        print("[ERROR] huggingface_hub is not installed")
        print("Installing huggingface_hub...")
        os.system(f"{sys.executable} -m pip install huggingface_hub")
        
        # 再試行
        print("Retrying download...")
        download_model()
        
    except Exception as e:
        print("=" * 60)
        print(f"[ERROR] Model download failed: {e}")
        print("=" * 60)
        sys.exit(1)

if __name__ == '__main__':
    download_model()
