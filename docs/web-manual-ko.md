# Docvert 웹 매뉴얼 (설치 및 사용 가이드)

Docvert는 복잡한 구조의 PDF 및 DOCX 문서를 읽어 시맨틱(Semantic) 마크다운으로 변환해주는 파이썬 기반 CLI 도구입니다.

이 문서는 **컴퓨터에 개발 환경(Homebrew, 파이썬 등)이 전혀 구축되어 있지 않은 완전 초기 상태**를 기준으로, 각 운영체제(OS)별 설치 및 실행 방법을 안내합니다.

---

## 🚀 가장 추천하는 방법: Docker를 이용한 설치 (모든 OS 공통)

Docvert는 내부적으로 AI 모델과 C언어 기반의 복잡한 시스템 라이브러리(poppler, tesseract 등)를 사용합니다. 따라서 OS에 직접 설치하는 것보다, **모든 것이 준비된 Docker 이미지를 사용하는 것이 가장 쉽고 안전**합니다.

1. **Docker 설치하기**
   - Windows/macOS: [Docker Desktop 다운로드 및 설치](https://www.docker.com/products/docker-desktop/)
   - 설치 후 Docker Desktop 프로그램을 실행해 주세요.

2. **Docvert 오프라인 릴리즈 다운로드**
   - Docvert [GitHub Releases 페이지](https://github.com/seonghobae/docvert/releases)에 접속하여 최신 버전의 `docvert-offline-release.tar.gz` (또는 분할된 `.part-*` 파일들)을 다운로드 받습니다.
   - 분할된 파일인 경우 먼저 터미널(또는 명령 프롬프트)에서 합쳐줍니다.
     ```bash
     cat docvert-offline-release.tar.gz.part-* > docvert-offline-release.tar.gz
     ```

3. **Docker 이미지 로드하기**
   - 다운로드 받은 경로에서 터미널을 열고 아래 명령어를 입력합니다.
     ```bash
     docker load -i docvert-offline.tar.gz
     ```

4. **변환 실행하기**
   - `input.pdf` 파일을 `out` 폴더로 변환하는 예시입니다. `$(pwd)`는 현재 폴더 위치를 의미합니다.
     ```bash
     docker run --rm \
         -v $(pwd):/data \
         docvert:offline convert /data/input.pdf --output-dir /data/out
     ```

---

## 💻 OS별 직접 설치 가이드 (Native Installation)

시스템에 직접 Docvert를 설치하고 싶으신 분들을 위한 가이드입니다. 

### 🍎 macOS 설치 가이드

Mac에 개발 환경이 전혀 없다는 가정 하에 진행합니다. 터미널(Terminal) 앱을 열고 순서대로 입력하세요.

**1. Command Line Tools 설치**
```bash
xcode-select --install
```
*(팝업이 뜨면 '설치'를 클릭하고 완료될 때까지 기다립니다.)*

**2. Homebrew(패키지 관리자) 설치**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
*(설치가 끝나면 화면 마지막에 나오는 `Next steps:` 안내에 따라 경로 추가 명령어를 복사해서 실행해야 합니다.)*

**3. 필수 시스템 라이브러리 설치**
```bash
brew install poppler tesseract libmagic
```

**4. 파이썬 초고속 패키지 관리자 `uv` 설치**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
*(설치 후 터미널을 완전히 껐다가 다시 켜주세요.)*

**5. Docvert 다운로드 및 설치**
```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

---

### 🪟 Windows 설치 가이드

Windows는 시스템 라이브러리(poppler 등) 호환성 문제로 인해, **WSL2(Windows Subsystem for Linux)** 사용을 강력히 권장합니다.

**1. WSL2 및 Ubuntu 설치**
- 시작 메뉴에서 `명령 프롬프트(cmd)` 또는 `PowerShell`을 찾아 **관리자 권한으로 실행**합니다.
```cmd
wsl --install
```
*(설치 후 컴퓨터를 재부팅합니다. 재부팅 후 자동으로 Ubuntu 창이 뜨면 사용자 이름과 비밀번호를 설정합니다.)*

**2. 필수 시스템 라이브러리 설치 (Ubuntu 터미널에서)**
```bash
sudo apt update
sudo apt install -y poppler-utils tesseract-ocr libmagic-dev curl
```

**3. 파이썬 초고속 패키지 관리자 `uv` 설치**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
*(설치 후 `source $HOME/.cargo/env` 를 입력하거나 터미널을 재시작합니다.)*

**4. Docvert 다운로드 및 설치**
```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

---

### 🐧 Linux (Ubuntu/Debian) 설치 가이드

**1. 필수 시스템 라이브러리 설치**
```bash
sudo apt update
sudo apt install -y poppler-utils tesseract-ocr libmagic-dev curl git
```

**2. 파이썬 초고속 패키지 관리자 `uv` 설치**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
*(설치 후 터미널을 재시작해 적용합니다.)*

**3. Docvert 다운로드 및 설치**
```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

---

## 🛠 사용 방법 (기본 명령어)

직접 설치를 마쳤다면 `uv run python -m docvert.cli.main` 명령어로 Docvert를 실행할 수 있습니다.

**1. 단일 파일 변환하기**
```bash
uv run python -m docvert.cli.main convert ./sample.pdf --output-dir ./results
```

**2. 폴더 내 모든 파일 일괄 변환 (배치 처리)**
```bash
uv run python -m docvert.cli.main batch ./my_documents --output-dir ./processed_docs
```

**3. LLM을 이용한 출력결과 교정 (선택사항)**
LLM(예: OpenAI)을 이용해 변환된 마크다운을 더 깔끔하게 다듬을 수 있습니다.
```bash
export OPENAI_API_KEY="여러분의-api-키"
uv run python -m docvert.cli.main convert ./sample.pdf --llm-refiner
```

자세한 내부 동작 원리 및 추가 옵션은 `docs/manual.md` 문서를 참고해 주세요.
