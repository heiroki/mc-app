# build/prepare_installer.py

import os
import shutil
from pathlib import Path

def prepare_installer():
    """インストーラー用のファイルを準備"""
    
    print("=" * 60)
    print("Preparing installer package...")
    print("=" * 60)
    
    # プロジェクトルート
    project_root = Path(__file__).parent.parent
    
    # インストーラーパッケージディレクトリ
    installer_pkg = project_root / 'installer' / 'package'
    
    # 既存のパッケージディレクトリをクリーンアップ
    if installer_pkg.exists():
        print(f"🗑️  Cleaning existing package directory: {installer_pkg}")
        shutil.rmtree(installer_pkg)
    
    installer_pkg.mkdir(parents=True, exist_ok=True)
    
    # ========================================
    # 1. Backend（PyInstallerビルド成果物）
    # ========================================
    print("\n[1/4] Copying Backend...")
    backend_src = project_root / 'dist' / 'backend_server.exe'
    backend_dst = installer_pkg / 'backend'
    backend_dst.mkdir(exist_ok=True)
    
    if backend_src.exists():
        shutil.copy2(backend_src, backend_dst / 'backend_server.exe')
        size_mb = backend_src.stat().st_size / (1024**2)
        print(f"   ✅ Backend copied: {size_mb:.1f} MB")
    else:
        print(f"   ❌ Backend not found: {backend_src}")
        print(f"   Please run PyInstaller first:")
        print(f"   pyinstaller build/backend_server.spec")
        raise FileNotFoundError(f"Backend executable not found: {backend_src}")
    
    # ========================================
    # 2. Flutter App（Flutter buildビルド成果物）
    # ========================================
    print("\n[2/4] Copying Flutter App...")
    flutter_src = project_root / 'frontend' / 'build' / 'windows' / 'runner' / 'Release'
    flutter_dst = installer_pkg / 'flutter_app'
    
    if flutter_src.exists():
        if flutter_dst.exists():
            shutil.rmtree(flutter_dst)
        shutil.copytree(flutter_src, flutter_dst)
        
        # 実行ファイル名を確認
        exe_files = list(flutter_dst.glob('*.exe'))
        if exe_files:
            print(f"   ✅ Flutter App copied")
            print(f"   Main executable: {exe_files[0].name}")
        else:
            print(f"   ⚠️  No .exe file found in Flutter build")
    else:
        print(f"   ❌ Flutter build not found: {flutter_src}")
        print(f"   Please run Flutter build first:")
        print(f"   cd frontend && flutter build windows --release")
        raise FileNotFoundError(f"Flutter build not found: {flutter_src}")
    
    # ========================================
    # 3. Models（GGUFモデルファイル）
    # ========================================
    print("\n[3/4] Copying Models...")
    models_src = project_root / 'models'
    models_dst = installer_pkg / 'models'
    models_dst.mkdir(exist_ok=True)
    
    model_files = list(models_src.glob('*.gguf')) if models_src.exists() else []
    
    if model_files:
        for model_file in model_files:
            shutil.copy2(model_file, models_dst / model_file.name)
            size_gb = model_file.stat().st_size / (1024**3)
            print(f"   ✅ {model_file.name}: {size_gb:.2f} GB")
    else:
        print(f"   ❌ No model files found in: {models_src}")
        print(f"   Please download model first:")
        print(f"   python build/download_model.py")
        raise FileNotFoundError(f"No model files found in: {models_src}")
    
    # ========================================
    # 4. Scripts（起動・停止スクリプト）
    # ========================================
    print("\n[4/4] Copying Scripts...")
    scripts_src = project_root / 'installer' / 'scripts'
    scripts_dst = installer_pkg / 'scripts'
    
    if scripts_src.exists():
        if scripts_dst.exists():
            shutil.rmtree(scripts_dst)
        shutil.copytree(scripts_src, scripts_dst)
        
        # スクリプトファイル一覧
        script_files = list(scripts_dst.glob('*.bat'))
        print(f"   ✅ Scripts copied ({len(script_files)} files)")
        for script in script_files:
            print(f"      - {script.name}")
    else:
        print(f"   ⚠️  Scripts directory not found: {scripts_src}")
        print(f"   Creating empty scripts directory...")
        scripts_dst.mkdir(exist_ok=True)
    
    # ========================================
    # 完了
    # ========================================
    print("\n" + "=" * 60)
    print("✅ Installer package prepared successfully!")
    print(f"📁 Location: {installer_pkg}")
    print("=" * 60)
    
    # パッケージ内容のサマリー
    print("\nPackage contents:")
    for item in installer_pkg.rglob('*'):
        if item.is_file():
            size_mb = item.stat().st_size / (1024**2)
            rel_path = item.relative_to(installer_pkg)
            if size_mb > 1:  # 1MB以上のファイルのみ表示
                print(f"   {rel_path}: {size_mb:.1f} MB")

if __name__ == '__main__':
    try:
        prepare_installer()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
