# DocVert 웹 매뉴얼 (설치 및 사용 가이드)

DocVert는 복잡한 구조의 PDF 및 DOCX 문서를 읽어 시맨틱(Semantic) 마크다운으로 변환해주는 파이썬 기반 CLI 도구입니다.

이 문서는 **컴퓨터에 개발 환경이 전혀 구축되어 있지 않은 완전 초기 상태**(Homebrew, 패키지 관리자, 파이썬 등 아무것도 없는 상태)를 기준으로, 각 운영체제(OS)별 설치 및 실행 방법을 안내합니다.

---

## Docker를 이용한 설치 (모든 OS 공통 — 가장 추천)

DocVert는 내부적으로 AI 모델과 C언어 기반의 복잡한 시스템 라이브러리(poppler, tesseract 등)를 사용합니다. 따라서 OS에 직접 설치하는 것보다, **모든 것이 준비된 Docker 이미지를 사용하는 것이 가장 쉽고 안전**합니다.

### 1단계: Docker 설치하기

각 OS별로 아래 설치 파일을 다운로드하여 설치하세요. **Homebrew나 별도 패키지 관리자가 필요 없습니다.**

| OS | 설치 방법 |
|---|---|
| **macOS** | [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/) 에서 `.dmg` 파일을 다운로드 → 더블클릭하여 설치 → Applications 폴더로 드래그 → Docker Desktop 실행 |
| **Windows** | [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) 에서 `.exe` 설치 파일 다운로드 → 실행하여 설치 → 재부팅 후 Docker Desktop 실행 |
| **Linux (Ubuntu/Debian)** | 아래 명령어를 터미널에 입력하세요 |

**Linux Docker 설치 (apt 이용):**
```bash
# Docker 공식 GPG 키 추가
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Docker 공식 저장소 추가
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker 설치
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 현재 사용자에게 Docker 권한 부여 (재로그인 필요)
sudo usermod -aG docker $USER
```

### 2단계: DocVert Docker 이미지 가져오기

**방법 A — 온라인 환경 (GitHub Releases에서 다운로드):**

[DocVert GitHub Releases 페이지](https://github.com/seonghobae/docvert/releases)에 접속하여 최신 버전의 분할 파일들(`docvert-offline-release.tar.gz.part-*`)을 모두 다운로드합니다.

```bash
# 분할 파일 합치기
cat docvert-offline-release.tar.gz.part-* > docvert-offline-release.tar.gz

# 압축 해제
tar -xzvf docvert-offline-release.tar.gz
cd docvert-offline-release

# Docker 이미지 로드
docker load -i docvert-offline.tar.gz

# 이미지 확인
docker images | grep docvert
```

**방법 B — 소스에서 직접 빌드:**

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
docker build -t docvert:offline .
```

### 3단계: 변환 실행하기

```bash
# 단일 파일 변환
docker run --rm \
    -v $(pwd):/data \
    docvert:offline convert /data/input.pdf --output-dir /data/out

# 폴더 내 모든 파일 일괄 변환
docker run --rm \
    -v $(pwd)/my_docs:/data/my_docs \
    -v $(pwd)/out:/data/out \
    docvert:offline batch /data/my_docs --output-dir /data/out
```

> **Windows PowerShell 사용 시:** `$(pwd)` 대신 `${PWD}` 를 사용하세요.
>
> **Windows CMD 사용 시:** `$(pwd)` 대신 `%cd%` 를 사용하세요.

---

## 폐쇄망(Air-gapped) 환경 설치

인터넷이 차단된 폐쇄망(보안망) 환경에서 DocVert를 사용하는 방법입니다.

### 준비 (인터넷이 되는 컴퓨터에서)

1. [DocVert GitHub Releases](https://github.com/seonghobae/docvert/releases)에서 최신 릴리즈의 모든 `.part-*` 파일을 다운로드합니다.
2. 다운로드한 파일들을 USB, CD, 보안 파일 전송 등을 통해 폐쇄망 내부 컴퓨터로 옮깁니다.

### 설치 (폐쇄망 컴퓨터에서)

**전제 조건:** 폐쇄망 컴퓨터에 Docker(또는 Podman)가 설치되어 있어야 합니다.

```bash
# 1. 분할 파일 합치기
cat docvert-offline-release.tar.gz.part-* > docvert-offline-release.tar.gz

# 2. 압축 해제
tar -xzvf docvert-offline-release.tar.gz
cd docvert-offline-release

# 3. Docker 이미지 로드
docker load -i docvert-offline.tar.gz

# 4. 이미지 확인
docker images | grep docvert
```

### 실행

```bash
# 단일 파일 변환
docker run --rm -v $(pwd):/data \
    docvert:offline convert /data/document.pdf --output-dir /data/out

# 폴더 일괄 변환
docker run --rm \
    -v $(pwd)/input:/data/input \
    -v $(pwd)/output:/data/output \
    docvert:offline batch /data/input --output-dir /data/output
```

> **참고:** Podman을 사용하는 환경에서는 `docker` 대신 `podman`을 입력하세요.

### 업데이트

새 버전이 나오면 Releases 페이지에서 새 `.part-*` 파일을 받아 같은 과정을 반복하면 됩니다. 기존 이미지는 자동으로 교체됩니다.

---

## macOS 직접 설치 (Homebrew 없이)

**Homebrew를 사용하지 않고** macOS에 직접 설치하는 방법입니다. 터미널(Terminal.app)을 열고 순서대로 진행하세요.

### 1단계: Command Line Tools 설치

```bash
xcode-select --install
```

팝업이 뜨면 **'설치'** 를 클릭하고 완료될 때까지 기다립니다. (이미 설치되어 있다면 건너뛰세요.)

### 2단계: 시스템 라이브러리 설치 (MacPorts 이용)

Homebrew 대신 [MacPorts](https://www.macports.org/install.php)를 사용합니다.

**MacPorts 설치:**

1. [MacPorts 다운로드 페이지](https://www.macports.org/install.php)에서 본인의 macOS 버전에 맞는 `.pkg` 설치 파일을 다운로드합니다.
2. 다운로드한 `.pkg` 파일을 더블클릭하여 설치합니다.
3. 터미널을 완전히 닫았다가 다시 열어 PATH가 적용되도록 합니다.

**필수 라이브러리 설치:**

```bash
sudo port install poppler tesseract libmagic
```

### 3단계: 파이썬 패키지 관리자 `uv` 설치

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치 후 터미널을 완전히 닫았다가 다시 열어주세요.

### 4단계: DocVert 다운로드 및 설치

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

### 5단계: 설치 확인

```bash
uv run python -m docvert.cli.main --help
```

> **대안: Conda를 이용한 설치**
>
> MacPorts 대신 [Miniconda](https://docs.anaconda.com/miniconda/install/)를 사용할 수도 있습니다.
>
> ```bash
> # Miniconda 설치 (웹에서 .pkg 다운로드하거나 아래 명령어)
> curl -fsSL https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh -o miniconda.sh
> bash miniconda.sh -b -p $HOME/miniconda
> eval "$($HOME/miniconda/bin/conda shell.bash hook)"
>
> # 필수 시스템 라이브러리 설치
> conda install -c conda-forge poppler tesseract libmagic
>
> # 이후 uv 설치 및 DocVert 설치는 동일
> ```

---

## Windows 직접 설치

Windows에서는 시스템 라이브러리 호환성 문제로 **WSL2(Windows Subsystem for Linux)** 사용을 강력히 권장합니다.

### 1단계: WSL2 및 Ubuntu 설치

시작 메뉴에서 **PowerShell** 또는 **명령 프롬프트(cmd)** 를 찾아 **관리자 권한으로 실행**합니다.

```cmd
wsl --install
```

설치 후 컴퓨터를 **재부팅**합니다. 재부팅 후 자동으로 Ubuntu 창이 열리면 사용자 이름과 비밀번호를 설정합니다.

> **참고:** Windows 10 버전 2004 이상 또는 Windows 11이 필요합니다. 이전 버전은 [수동 설치 가이드](https://learn.microsoft.com/ko-kr/windows/wsl/install-manual)를 참고하세요.

### 2단계: 필수 시스템 라이브러리 설치

Ubuntu 터미널(WSL)에서 아래 명령어를 입력합니다.

```bash
sudo apt update
sudo apt install -y poppler-utils tesseract-ocr libmagic-dev curl git
```

### 3단계: 파이썬 패키지 관리자 `uv` 설치

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치 후 아래 명령어를 실행하거나 터미널을 재시작합니다.

```bash
source $HOME/.local/bin/env
```

### 4단계: DocVert 다운로드 및 설치

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

### 5단계: 설치 확인

```bash
uv run python -m docvert.cli.main --help
```

### Windows 파일 접근 팁

WSL에서 Windows 파일에 접근하려면 `/mnt/c/` 경로를 사용합니다.

```bash
# 예: 바탕화면의 파일 변환
uv run python -m docvert.cli.main convert \
    "/mnt/c/Users/사용자이름/Desktop/document.pdf" \
    --output-dir ./results
```

---

## Linux (Ubuntu/Debian) 직접 설치

### 1단계: 필수 시스템 라이브러리 설치

```bash
sudo apt update
sudo apt install -y poppler-utils tesseract-ocr libmagic-dev curl git
```

### 2단계: 파이썬 패키지 관리자 `uv` 설치

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치 후 터미널을 재시작해 적용합니다.

### 3단계: DocVert 다운로드 및 설치

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

### 4단계: 설치 확인

```bash
uv run python -m docvert.cli.main --help
```

---

## Linux (RHEL/CentOS/Fedora) 직접 설치

### 1단계: 필수 시스템 라이브러리 설치

**Fedora:**
```bash
sudo dnf install -y poppler-utils tesseract libmagic curl git
```

**RHEL / CentOS / Rocky Linux / AlmaLinux:**
```bash
sudo dnf install -y epel-release
sudo dnf install -y poppler-utils tesseract libmagic curl git
```

### 2단계: 파이썬 패키지 관리자 `uv` 설치

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치 후 터미널을 재시작합니다.

### 3단계: DocVert 다운로드 및 설치

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

### 4단계: 설치 확인

```bash
uv run python -m docvert.cli.main --help
```

---

## 사용 방법 (기본 명령어)

직접 설치를 마쳤다면 `uv run python -m docvert.cli.main` 명령어로 DocVert를 실행할 수 있습니다.

### 단일 파일 변환

```bash
uv run python -m docvert.cli.main convert ./sample.pdf --output-dir ./results
```

### 폴더 내 모든 파일 일괄 변환 (배치 처리)

```bash
uv run python -m docvert.cli.main batch ./my_documents --output-dir ./processed_docs
```

### 배치 처리 옵션

```bash
# 오류가 발생해도 계속 진행 + 캐시 사용
uv run python -m docvert.cli.main batch ./my_documents \
    --output-dir ./processed_docs \
    --continue-on-error \
    --cache
```

### 출력 결과물

변환 후 각 파일마다 3가지가 생성됩니다:

| 파일 | 설명 |
|---|---|
| `document.md` | 변환된 마크다운 파일 |
| `document.conversion.json` | 변환 메타데이터 (파서 정보, 신뢰도 점수, 경고사항 등) |
| `document.assets/` | 추출된 이미지 등 에셋 폴더 |

---

## LLM 교정 기능 설정

DocVert는 `litellm`을 기반으로 다양한 LLM 제공자를 지원합니다. LLM을 이용하면 변환된 마크다운을 더 깔끔하게 교정할 수 있습니다.

### OpenAI 사용

```bash
export OPENAI_API_KEY="여러분의-api-키"
uv run python -m docvert.cli.main convert ./sample.pdf --llm-refiner
```

### Vertex AI (Google Cloud) 사용

```bash
export VERTEX_PROJECT="여러분의-google-project"
export VERTEX_LOCATION="us-central1"
# gcloud auth application-default login 으로 인증 필요
uv run python -m docvert.cli.main convert ./sample.pdf --llm-refiner
```

### 로컬 LLM (Ollama 등) 사용

인터넷 없이도 로컬에서 LLM 교정을 사용할 수 있습니다.

```bash
export OPENAI_API_KEY="dummy"
export OPENAI_BASE_URL="http://localhost:11434/v1"
uv run python -m docvert.cli.main convert ./sample.pdf --llm-refiner
```

자세한 LLM 설정 방법은 [litellm 공식 문서](https://docs.litellm.ai/)를 참고하세요.

---

## 문제 해결

### `poppler` 관련 오류

```
pdfinfo not found. Install poppler-utils.
```

- **macOS (MacPorts):** `sudo port install poppler`
- **macOS (Conda):** `conda install -c conda-forge poppler`
- **Ubuntu/Debian:** `sudo apt install -y poppler-utils`
- **Fedora:** `sudo dnf install -y poppler-utils`
- **Docker:** Docker 이미지에는 이미 포함되어 있습니다.

### `tesseract` 관련 오류

```
tesseract is not installed or not in PATH
```

- **macOS (MacPorts):** `sudo port install tesseract`
- **macOS (Conda):** `conda install -c conda-forge tesseract`
- **Ubuntu/Debian:** `sudo apt install -y tesseract-ocr`
- **Fedora:** `sudo dnf install -y tesseract`

### Python 버전 문제

DocVert는 Python 3.14 이상이 필요합니다. `uv`가 자동으로 적절한 Python 버전을 관리합니다.

```bash
# uv가 관리하는 Python 버전 확인
uv python list
```

### WSL2 관련 (Windows)

WSL이 설치되지 않는 경우, Windows 기능에서 **"Linux용 Windows 하위 시스템"** 과 **"가상 머신 플랫폼"** 이 활성화되어 있는지 확인하세요.

```cmd
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

이후 재부팅 후 `wsl --install` 을 다시 시도하세요.
