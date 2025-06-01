import os
import subprocess
import sys
import webbrowser
import time

# 1. 시스템 pip 경로 설정 (가상환경을 사용하지 않는 경우)
pip_path = "pip"
python_path = sys.executable  # 현재 실행 중인 Python 사용 

# 2. 패키지 설치
def install_packages():
    print("필요한 패키지를 설치합니다...")
    packages = ["torch", "transformers", "django", "requests", "pandas"]

    for pkg in packages:
        print(f"{pkg} 설치 중...")
        subprocess.check_call([pip_path, "install", pkg])
        print(f"{pkg} 설치 완료")

# 3. 모델 다운로드 스크립트 실행 (있는지 검사)
def run_download_model():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "finetuned_model")
    
    if os.path.exists(model_path):
        print("'finetuned_model' 폴더가 이미 존재합니다. 다운로드를 생략합니다.")
        return

    download_model_path = os.path.join(script_dir, "download_model.py")
    if os.path.exists(download_model_path):
        print("모델 다운로드 스크립트를 실행합니다...")
        subprocess.check_call([python_path, download_model_path])
        print("모델 다운로드 완료")
    else:
        print("download_model.py 파일이 없습니다. 건너뜁니다.")
        input("엔터를 누르면 종료됩니다.")

# 4. 서버 실행 및 브라우저 열기
def run_server_and_open_browser():
    print("로컬 Django 서버를 실행합니다...")
    try:
        server_process = subprocess.Popen(
            [python_path, "manage.py", "runserver"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        print("브라우저를 엽니다 (http://127.0.0.1:8000/)")
        time.sleep(3)
        webbrowser.open("http://127.0.0.1:8000/")

        # 서버가 죽지 않도록 대기
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("서버 종료 요청됨 (Ctrl+C)")
            server_process.terminate()
    except Exception as e:
        print(f"서버 실행 중 오류 발생: {e}")
        # (옵션) 만약 서버가 아예 시작 못한 경우, 에러 메시지 표기
        if 'server_process' in locals():
            out, err = server_process.communicate(timeout=2)
            print("---- 서버 출력 ----")
            print(out.decode(errors="ignore"))
            print("---- 서버 에러 ----")
            print(err.decode(errors="ignore"))

# 전체 실행 흐름
if __name__ == "__main__":
    install_packages()
    run_download_model()
    run_server_and_open_browser()
