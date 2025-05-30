import os
import subprocess
import sys
from zipfile import ZipFile, BadZipFile

# 필요한 패키지 목록
required_packages = ['gdown']

# 패키지 설치 또는 업그레이드 함수
def install_or_upgrade(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])

# 패키지 자동 설치/업그레이드
for package in required_packages:
    try:
        __import__(package)
        print(f"{package} found. Upgrading to latest version...")
        install_or_upgrade(package)
    except ImportError:
        print(f"{package} not found. Installing...")
        install_or_upgrade(package)

# 다운로드 및 압축 해제 정보
file_id = "1ce8FiW8QOqC5AdmGOp7-uY1KGiOpzyjR"
output_path = "model.zip"
model_dir = "./finetuned_model"

# 모델이 없으면 다운로드 후 압축 해제
if not os.path.exists(model_dir):
    if not os.path.exists(output_path):
        print("⬇️ Downloading model with gdown CLI...")
        exit_code = os.system(f"gdown --id {file_id} -O {output_path}")
        if exit_code != 0 or not os.path.exists(output_path):
            raise RuntimeError("❌ gdown CLI failed to download the file.")

    print("📦 Unzipping model...")
    try:
        with ZipFile(output_path, 'r') as zip_ref:
            zip_ref.extractall(model_dir)
        os.remove(output_path)
        print("✅ Done.")
    except BadZipFile:
        raise RuntimeError("❌ 압축 해제 실패: 다운로드된 파일이 ZIP 형식이 아닙니다.")
else:
    print("✅ Model already exists.")
