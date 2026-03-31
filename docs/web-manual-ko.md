# DocVert 사용 설명서

> DocVert는 PDF나 워드(DOCX) 파일을 깔끔한 마크다운(.md) 파일로 변환해주는 도구입니다.
> 이 문서는 **컴퓨터에 아무것도 설치되어 있지 않은 분**을 위해 작성되었습니다.

---

## 어떤 설치 방법을 선택해야 하나요?

아래 표를 보고 본인에게 맞는 방법을 선택하세요.

| 상황 | 추천 설치 방법 | 난이도 |
|---|---|---|
| macOS를 사용하고 있다 | [방법 A: macOS에 직접 설치](#방법-a-macos에-직접-설치) | 쉬움 |
| Windows를 사용하고 있다 | [방법 B: Windows에 직접 설치](#방법-b-windows에-직접-설치) | 보통 |
| Linux를 사용하고 있다 | [방법 C: Linux에 직접 설치](#방법-c-linux에-직접-설치) | 쉬움 |
| 인터넷이 안 되는 폐쇄망이다 | [방법 D: 폐쇄망 설치](#방법-d-폐쇄망air-gapped-환경-설치) | 보통 |
| Docker를 이미 사용하고 있다 | [방법 E: Docker로 설치](#방법-e-docker로-설치-docker-사용자-전용) | 쉬움 |

> **참고:** Docker Desktop은 설치 후 항상 백그라운드에서 메모리를 2~4GB 이상 점유합니다. Docker를 이미 사용하지 않는다면 **직접 설치 방법을 추천**합니다.

---

## 방법 A: macOS에 직접 설치

Mac을 처음 쓰시는 분도 따라할 수 있도록 하나씩 설명합니다.

### A-1. 터미널 열기

1. `Cmd + Space` 를 눌러 **Spotlight 검색**을 엽니다.
2. `터미널` 이라고 입력합니다.
3. **터미널(Terminal)** 앱을 클릭하여 실행합니다.

> 터미널은 컴퓨터에 텍스트 명령어를 입력하는 프로그램입니다.
> 앞으로 모든 명령어는 이 터미널에 붙여넣기(`Cmd + V`)하면 됩니다.

### A-2. Command Line Tools 설치

터미널에 아래를 붙여넣고 Enter를 누릅니다:

```bash
xcode-select --install
```

팝업 창이 뜨면 **'설치'** 버튼을 클릭합니다. 설치가 완료될 때까지 기다리세요 (5~10분 소요).

> 이미 설치되어 있다면 "already installed"라는 메시지가 나옵니다. 그냥 다음 단계로 넘어가세요.

### A-3. Homebrew 설치 (방법 1 — 추천)

Homebrew는 Mac에서 프로그램을 쉽게 설치할 수 있는 도구입니다.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

설치가 끝나면 화면 마지막에 **`Next steps:`** 라는 안내가 나옵니다. 거기에 나오는 명령어 2줄을 복사해서 실행해야 합니다. 보통 아래와 비슷합니다:

```bash
echo >> ~/.zprofile
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

> **확인 방법:** `brew --version` 을 입력해서 버전 번호가 나오면 성공입니다.

### A-3 대안. Homebrew 없이 설치하기 (방법 2)

Homebrew를 사용하고 싶지 않다면 [MacPorts](https://www.macports.org/install.php)를 사용할 수 있습니다.

1. [MacPorts 다운로드 페이지](https://www.macports.org/install.php)에서 본인 macOS 버전에 맞는 `.pkg` 파일을 다운로드합니다.
2. 다운로드한 파일을 더블클릭하여 설치합니다.
3. 터미널을 완전히 닫았다가 다시 엽니다.

### A-4. 필수 프로그램 설치

**Homebrew를 설치한 경우:**
```bash
brew install poppler tesseract libmagic
```

**MacPorts를 설치한 경우:**
```bash
sudo port install poppler tesseract libmagic
```

> 이 프로그램들은 PDF에서 텍스트를 추출하고, 이미지 속 글자를 인식(OCR)하는 데 필요합니다.

### A-5. uv 설치 (파이썬 패키지 관리자)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치 후 **터미널을 완전히 닫았다가 다시 열어주세요** (반드시!).

> `uv`는 DocVert에 필요한 파이썬 환경을 자동으로 관리해주는 도구입니다.
> 파이썬을 별도로 설치할 필요가 없습니다. `uv`가 알아서 다운로드합니다.

### A-6. DocVert 다운로드

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

> `git clone`은 인터넷에서 DocVert 프로그램을 다운로드하는 명령어입니다.
> `uv sync`는 DocVert가 필요로 하는 모든 라이브러리를 자동으로 설치합니다. 처음에는 몇 분 걸릴 수 있습니다.

### A-7. 설치 확인

```bash
uv run python -m docvert.cli.main --help
```

사용 가능한 명령어 목록이 출력되면 설치 성공입니다! [사용 방법](#사용-방법)으로 이동하세요.

---

## 방법 B: Windows에 직접 설치

Windows에서는 **WSL2(Windows Subsystem for Linux)** 를 통해 리눅스 환경을 만들어서 사용합니다.

### B-1. WSL2 설치

1. **시작 메뉴**에서 `PowerShell` 을 검색합니다.
2. **"관리자 권한으로 실행"** 을 클릭합니다.
3. 아래 명령어를 붙여넣고 Enter를 누릅니다:

```cmd
wsl --install
```

4. 설치가 완료되면 **컴퓨터를 재부팅**합니다.
5. 재부팅 후 자동으로 Ubuntu 창이 열립니다.
6. **사용자 이름**과 **비밀번호**를 설정합니다 (비밀번호는 화면에 표시되지 않지만 정상입니다).

> **Windows 10 버전 2004 이상** 또는 **Windows 11**이 필요합니다.
> 버전 확인: `시작 → 설정 → 시스템 → 정보 → Windows 사양`

### B-2. 필수 프로그램 설치

Ubuntu 터미널에서 아래를 한 줄씩 실행합니다:

```bash
sudo apt update
```

비밀번호를 물으면 B-1에서 설정한 비밀번호를 입력합니다.

```bash
sudo apt install -y poppler-utils tesseract-ocr libmagic-dev curl git
```

### B-3. uv 설치

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치 후 아래를 실행합니다:

```bash
source $HOME/.local/bin/env
```

### B-4. DocVert 다운로드

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

### B-5. 설치 확인

```bash
uv run python -m docvert.cli.main --help
```

### B-6. Windows 파일을 변환하고 싶을 때

WSL에서 Windows의 파일에 접근하려면 `/mnt/c/` 경로를 사용합니다.

예를 들어, 바탕화면에 있는 `보고서.pdf`를 변환하려면:

```bash
uv run python -m docvert.cli.main convert \
    "/mnt/c/Users/내이름/Desktop/보고서.pdf" \
    --output-dir ./결과
```

> `내이름` 부분을 실제 Windows 사용자 이름으로 바꿔주세요.
> 사용자 이름을 모르면 Windows 탐색기에서 `C:\Users\` 폴더를 열어 확인하세요.

---

## 방법 C: Linux에 직접 설치

### Ubuntu / Debian 계열

```bash
# 1. 필수 프로그램 설치
sudo apt update
sudo apt install -y poppler-utils tesseract-ocr libmagic-dev curl git

# 2. uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# 3. DocVert 다운로드 및 설치
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync

# 4. 설치 확인
uv run python -m docvert.cli.main --help
```

### Fedora / RHEL / CentOS / Rocky Linux

```bash
# 1. 필수 프로그램 설치
sudo dnf install -y poppler-utils tesseract libmagic curl git

# 2. uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# 3. DocVert 다운로드 및 설치
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync

# 4. 설치 확인
uv run python -m docvert.cli.main --help
```

---

## 방법 D: 폐쇄망(Air-gapped) 환경 설치

인터넷이 차단된 보안망에서 DocVert를 사용하는 방법입니다. Docker(또는 Podman)가 필요합니다.

### 준비물

- 인터넷이 되는 컴퓨터 1대
- USB 메모리 또는 보안 파일 전송 수단
- 폐쇄망 컴퓨터에 Docker 또는 Podman이 설치되어 있어야 합니다

### 인터넷이 되는 컴퓨터에서

1. [DocVert GitHub Releases](https://github.com/seonghobae/docvert/releases) 페이지에 접속합니다.
2. 최신 버전의 **모든 `.part-*` 파일**을 다운로드합니다 (여러 개의 파일로 나뉘어 있습니다).
3. 다운로드한 파일들을 USB 등으로 폐쇄망 컴퓨터에 옮깁니다.

### 폐쇄망 컴퓨터에서

```bash
# 1. 다운로드한 파일들이 있는 폴더로 이동
cd /path/to/downloaded/files

# 2. 분할 파일 합치기
cat docvert-offline-release.tar.gz.part-* > docvert-offline-release.tar.gz

# 3. 압축 해제
tar -xzvf docvert-offline-release.tar.gz
cd docvert-offline-release

# 4. Docker 이미지 설치
docker load -i docvert-offline.tar.gz

# 5. 설치 확인
docker images | grep docvert
```

> `docvert   offline` 이라는 줄이 보이면 성공입니다.

사용법은 [Docker로 사용하기](#docker로-사용하기) 섹션을 참고하세요.

---

## 방법 E: Docker로 설치 (Docker 사용자 전용)

> **주의:** Docker Desktop은 설치 후 항상 백그라운드에서 **메모리를 2~4GB 이상 점유**합니다.
> Docker를 이미 사용하고 있지 않다면, 위의 직접 설치 방법(방법 A, B, C)을 추천합니다.

Docker가 이미 설치되어 있다면:

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
docker build -t docvert:offline .
```

---

## 사용 방법

설치를 마쳤다면 이제 문서를 변환할 수 있습니다!

### PDF 파일 하나 변환하기

변환할 파일이 있는 폴더에서 터미널을 열고:

```bash
uv run python -m docvert.cli.main convert ./내문서.pdf --output-dir ./결과
```

> **뜻 풀이:**
>
> - `convert` — "변환해라"
> - `./내문서.pdf` — 변환할 파일 경로
> - `--output-dir ./결과` — 결과를 저장할 폴더 (없으면 자동 생성)

### 워드(DOCX) 파일 변환하기

```bash
uv run python -m docvert.cli.main convert ./보고서.docx --output-dir ./결과
```

### 폴더 안의 모든 파일 한꺼번에 변환하기

```bash
uv run python -m docvert.cli.main batch ./문서폴더 --output-dir ./결과폴더
```

> `batch`는 지정한 폴더 안에 있는 모든 PDF, DOCX 파일을 자동으로 찾아서 변환합니다.

### 변환 결과물 확인

변환이 완료되면 결과 폴더에 파일마다 3가지가 생깁니다:

| 파일 | 설명 |
|---|---|
| `파일이름.md` | 변환된 마크다운 파일 (텍스트 편집기로 열 수 있음) |
| `파일이름.conversion.json` | 변환 정보 (어떤 파서가 사용되었는지, 경고사항 등) |
| `파일이름.assets/` | 문서에 포함된 이미지가 저장된 폴더 |

### Docker로 사용하기

Docker를 사용하는 경우 명령어가 조금 다릅니다:

```bash
# 현재 폴더의 파일을 변환
docker run --rm -v "$(pwd)":/data docvert:offline convert /data/내문서.pdf --output-dir /data/결과

# 폴더 일괄 변환
docker run --rm -v "$(pwd)":/data docvert:offline batch /data/문서폴더 --output-dir /data/결과폴더
```

> **Windows PowerShell:** `$(pwd)` 대신 `${PWD}` 를 사용하세요.

---

## 고급: LLM으로 결과 교정하기 (선택사항)

AI를 이용해서 변환 결과를 더 깔끔하게 다듬을 수 있습니다. 이 기능은 선택사항이며, 사용하려면 API 키가 필요합니다.

### OpenAI 사용 시

```bash
# 1. API 키 설정 (https://platform.openai.com/api-keys 에서 발급)
export OPENAI_API_KEY="sk-여러분의키를여기에붙여넣으세요"

# 2. LLM 교정을 켜고 변환
uv run python -m docvert.cli.main convert ./내문서.pdf --output-dir ./결과 --llm-refiner
```

### 로컬 AI (Ollama) 사용 시 — 인터넷 없이 가능

[Ollama](https://ollama.com/)를 설치하면 인터넷 없이도 AI 교정을 사용할 수 있습니다.

```bash
# 1. Ollama 설치 후 모델 다운로드 (한 번만)
ollama pull llama3

# 2. 환경변수 설정
export OPENAI_API_KEY="dummy"
export OPENAI_BASE_URL="http://localhost:11434/v1"

# 3. LLM 교정 실행
uv run python -m docvert.cli.main convert ./내문서.pdf --output-dir ./결과 --llm-refiner
```

---

## 자주 묻는 질문 (FAQ)

### Q: "command not found: uv" 라고 나와요

터미널을 완전히 닫았다가 다시 여세요. 그래도 안 되면:

```bash
source $HOME/.local/bin/env
```

### Q: "pdfinfo not found" 라고 나와요

PDF 관련 프로그램이 설치되지 않은 것입니다:

- **macOS (Homebrew):** `brew install poppler`
- **macOS (MacPorts):** `sudo port install poppler`
- **Ubuntu/Debian:** `sudo apt install -y poppler-utils`
- **Fedora/RHEL:** `sudo dnf install -y poppler-utils`

### Q: "tesseract is not installed" 라고 나와요

OCR 프로그램이 설치되지 않은 것입니다:

- **macOS (Homebrew):** `brew install tesseract`
- **macOS (MacPorts):** `sudo port install tesseract`
- **Ubuntu/Debian:** `sudo apt install -y tesseract-ocr`
- **Fedora/RHEL:** `sudo dnf install -y tesseract`

### Q: 파이썬을 별도로 설치해야 하나요?

아니요. `uv`가 필요한 파이썬 버전을 자동으로 다운로드하고 관리합니다. 별도로 파이썬을 설치할 필요가 없습니다.

### Q: WSL이 뭔가요?

WSL(Windows Subsystem for Linux)은 Windows 안에서 리눅스를 사용할 수 있게 해주는 기능입니다. 별도의 가상머신 없이 Windows 안에서 바로 리눅스 명령어를 사용할 수 있습니다.

### Q: 변환 결과의 품질이 아쉬워요

`--llm-refiner` 옵션을 사용하면 AI가 결과를 교정해줍니다. [LLM으로 결과 교정하기](#고급-llm으로-결과-교정하기-선택사항) 섹션을 참고하세요.

### Q: 업데이트는 어떻게 하나요?

DocVert가 설치된 폴더에서:

```bash
cd docvert
git pull
uv sync
```
