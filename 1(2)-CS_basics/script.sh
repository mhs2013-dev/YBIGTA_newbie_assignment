# anaconda(또는 miniconda)가 존재하지 않을 경우 설치해주세요!
## TODO
if [ -z "${BASH_VERSION:-}" ]; then
    exec bash "$0" "$@"
fi

if ! command -v conda >/dev/null 2>&1; then
    echo "[INFO] conda 미설치: Miniconda 설치를 진행합니다."

    MINICONDA_DIR="$HOME/miniconda3"
    INSTALLER="$HOME/miniconda_installer.sh"
    URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"

    if [ ! -d "$MINICONDA_DIR" ]; then
        if command -v curl >/dev/null 2>&1; then
            curl -fsSL "$URL" -o "$INSTALLER" || { echo "[INFO] Miniconda 다운로드 실패"; exit 1; }
        fi

        if [ ! -f "$INSTALLER" ]; then
            if command -v wget >/dev/null 2>&1; then
                wget -qO "$INSTALLER" "$URL" || { echo "[INFO] Miniconda 다운로드 실패"; exit 1; }
            fi
        fi

        if [ ! -f "$INSTALLER" ]; then
            echo "[INFO] curl/wget이 없어 Miniconda 설치 파일을 다운로드할 수 없습니다."
            exit 1
        fi

        bash "$INSTALLER" -b -p "$MINICONDA_DIR" || { echo "[INFO] Miniconda 설치 실패"; exit 1; }
        rm -f "$INSTALLER"
    fi

    export PATH="$MINICONDA_DIR/bin:$PATH"
fi


# Conda 환셩 생성 및 활성화
## TODO
CONDA_BASE="$(conda info --base 2>/dev/null)"
if [ -z "$CONDA_BASE" ] || [ ! -f "$CONDA_BASE/etc/profile.d/conda.sh" ]; then
    echo "[INFO] conda 초기화 스크립트를 찾을 수 없습니다: $CONDA_BASE"
    exit 1
fi

# conda activate가 스크립트에서도 동작하도록 초기화
# shellcheck source=/dev/null
source "$CONDA_BASE/etc/profile.d/conda.sh"
if conda tos --help >/dev/null 2>&1; then
    yes | conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main >/dev/null 2>&1 || true
    yes | conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r >/dev/null 2>&1 || true
fi

# myenv가 없으면 생성
if ! conda env list | awk '{print $1}' | grep -qx "myenv"; then
    conda create -y -n myenv python=3.11 || { echo "[INFO] myenv 생성 실패"; exit 1; }
fi

conda activate myenv || { echo "[INFO] myenv 활성화 실패"; exit 1; }


## 건드리지 마세요! ##
python_env=$(python -c "import sys; print(sys.prefix)")
if [[ "$python_env" == *"/envs/myenv"* ]]; then
    echo "[INFO] 가상환경 활성화: 성공"
else
    echo "[INFO] 가상환경 활성화: 실패"
    exit 1 
fi

# 필요한 패키지 설치
## TODO
# 디렉토리 확인/생성
[ -d "input" ] || { echo "[INFO] input 디렉토리가 없습니다."; exit 1; }
[ -d "submission" ] || { echo "[INFO] submission 디렉토리가 없습니다."; exit 1; }
mkdir -p output

# submission에 .py가 존재하는지 사전 점검(없으면 채점 조건 자체 불만족)
shopt -s nullglob
py_files=(submission/*.py)
if [ ${#py_files[@]} -eq 0 ]; then
    echo "[INFO] submission/*.py 파일이 없습니다."
    exit 1
fi

python -m pip install --upgrade pip || { echo "[INFO] pip 업그레이드 실패"; exit 1; }
python -m pip install mypy || { echo "[INFO] mypy 설치 실패"; exit 1; }


# Submission 폴더 파일 실행
cd submission || { echo "[INFO] submission 디렉토리로 이동 실패"; exit 1; }

for file in *.py; do
    ## TODO
    prob="${file%.py}"
    in_file="../input/${prob}_input"
    out_file="../output/${prob}_output"

    if [ ! -f "$in_file" ]; then
        echo "[INFO] 입력 파일이 없습니다: $in_file"
        exit 1
    fi

    python "$file" < "$in_file" > "$out_file" || { echo "[INFO] 실행 실패: $file"; exit 1; }
    echo "[INFO] 실행 완료: $file -> $out_file"

done

# mypy 테스트 실행 및 mypy_log.txt 저장
## TODO
cd .. || { echo "[INFO] 상위 디렉토리 이동 실패"; exit 1; }

mypy submission/*.py > mypy_log.txt 2>&1
mypy_status=$?
if [ $mypy_status -ne 0 ]; then
    echo "[INFO] mypy 테스트 실패 (mypy_log.txt 확인)"
    exit 1
else
    echo "[INFO] mypy 테스트 통과"
fi

# conda.yml 파일 생성
## TODO
conda env export -n myenv --no-builds > conda.yml || { echo "[INFO] conda.yml 생성 실패"; exit 1; }

# 가상환경 비활성화
## TODO
conda deactivate || true
