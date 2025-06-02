import os
import subprocess
import sys

# 필요한 패키지 목록
required_packages = ['gdown']

# 패키지 설치 함수
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# 패키지 자동 설치
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"{package} not found. Installing...")
        install(package)

# 이제 gdown을 사용할 수 있음
import gdown
from zipfile import ZipFile  # 표준 라이브러리라 별도 설치 필요 없음

# 모델 다운로드
file_id = "1ouj2cfQoCXwa46tO9L8DLJhkbfaH3irS"  # ← 여기에 Drive 파일 ID 넣기
url = f"https://drive.google.com/uc?id={file_id}"

output_path = "model.zip"
model_dir = "./finetuned_model"

# 이미 존재하면 스킵
if not os.path.exists(model_dir):
    print("Downloading model...")
    gdown.download(url, output_path, quiet=False)

    print("Unzipping model...")
    with ZipFile(output_path, 'r') as zip_ref:
        zip_ref.extractall(model_dir)
    os.remove(output_path)
else:
    print("Model already exists.")
