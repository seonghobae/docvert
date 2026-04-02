# DocVert 사용 설명서

## DocVert가 뭔가요?

회사에서 받은 PDF 보고서나 워드(DOCX) 파일이 있다고 해보세요. 이런 파일 속의 내용을 **텍스트 파일**로 깔끔하게 뽑아주는 도구가 DocVert입니다.

변환된 결과는 **마크다운(.md)** 이라는 형식으로 저장됩니다. 마크다운은 메모장으로도 열 수 있는 단순한 텍스트 파일인데, 제목, 표, 목록 같은 문서 구조가 그대로 유지됩니다.

**이런 경우에 유용합니다:**

- PDF 속 텍스트를 복사하고 싶은데 깨지는 경우
- 워드 파일을 다른 시스템에서 사용할 수 있는 형식으로 바꾸고 싶은 경우
- 많은 문서를 한꺼번에 텍스트로 변환해야 하는 경우

---

## 시작하기 전에 알아야 할 것

### "터미널"이란?

컴퓨터에 명령어를 글자로 입력하는 프로그램입니다. 마우스로 클릭하는 대신, 글자를 입력해서 컴퓨터에게 지시하는 방식입니다.

처음에는 낯설 수 있지만, 이 설명서에 나오는 명령어를 **그대로 복사해서 붙여넣기만 하면** 됩니다. 직접 타이핑할 필요가 거의 없습니다.

### "복사 → 붙여넣기" 방법

| 운영체제 | 복사 | 붙여넣기 |
|---|---|---|
| Mac | `Cmd + C` | `Cmd + V` |
| Windows (WSL 터미널) | 드래그로 선택하면 자동 복사 | 마우스 오른쪽 클릭 |
| Linux | `Ctrl + Shift + C` | `Ctrl + Shift + V` |

> **중요:** 터미널에서는 `Ctrl + C`가 복사가 아니라 "실행 중인 프로그램 중지" 입니다!
> Linux나 Windows WSL에서 복사하려면 반드시 `Ctrl + Shift + C`를 사용하세요.

### 명령어 입력 후에는?

명령어를 붙여넣은 뒤 **Enter(엔터) 키**를 눌러야 실행됩니다.

### 비밀번호를 입력할 때

`sudo` 라는 명령어를 사용하면 비밀번호를 물어봅니다. 비밀번호를 입력할 때 **화면에 아무것도 표시되지 않는 것이 정상**입니다 (별표(\*)도 안 나옵니다). 그냥 비밀번호를 입력하고 Enter를 누르면 됩니다.

---

## 어떤 설치 방법을 선택하나요?

| 내 컴퓨터 | 추천 설치 방법 |
|---|---|
| **Mac**을 사용합니다 | [Mac 설치 안내](#mac-설치-안내)로 이동 |
| **Windows**를 사용합니다 | [Windows 설치 안내](#windows-설치-안내)로 이동 |
| **Linux**를 사용합니다 | [Linux 설치 안내](#linux-설치-안내)로 이동 |
| **인터넷이 안 됩니다** (폐쇄망) | [폐쇄망 설치 안내](#폐쇄망-설치-안내)로 이동 |

> **Docker Desktop에 대해:** Docker Desktop이라는 프로그램을 이용하는 방법도 있지만, 이 프로그램은 설치하면 컴퓨터를 켤 때마다 **메모리(RAM)를 2~4GB 이상 항상 차지**합니다. 일반 사용자에게는 부담이 크므로, 이 설명서에서는 **Docker 없이 직접 설치하는 방법을 기본으로 안내**합니다. 폐쇄망(인터넷이 안 되는 환경)에서만 Docker를 사용합니다.

---

## Mac 설치 안내

### 1단계: 터미널 열기

1. 키보드에서 `Cmd + Space` 를 동시에 누릅니다 (화면 중앙에 검색창이 나타남).
2. `터미널` 이라고 입력합니다.
3. **터미널(Terminal)** 이라고 나오는 항목을 클릭합니다.

> 검은색 (또는 흰색) 배경에 글자가 깜빡이는 창이 열리면 성공입니다.
> 앞으로 모든 명령어는 이 창에 붙여넣습니다.

### 2단계: 개발 도구 설치

아래 명령어를 터미널에 붙여넣고 Enter를 누릅니다:

```bash
xcode-select --install
```

**화면에 나타나는 것:** 팝업 창이 뜹니다.

**해야 할 것:** "설치" 버튼을 클릭하고 기다립니다 (5~10분).

**이미 설치되어 있으면:** `error: command line tools are already installed` 이라고 나옵니다. 정상입니다. 다음 단계로 넘어가세요.

### 3단계: Homebrew 설치

Homebrew는 Mac에서 프로그램을 쉽게 설치하고 관리할 수 있게 해주는 도구입니다. 아래를 통째로 복사해서 붙여넣으세요:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**화면에 나타나는 것:** 설치 진행 과정이 쭉 표시됩니다. 중간에 비밀번호를 물어보면 Mac 로그인 비밀번호를 입력합니다.

**설치가 끝나면:** 화면 하단에 `==> Next steps:` 라고 나옵니다. 그 아래에 나오는 명령어를 **반드시** 복사해서 실행해야 합니다. 보통 이렇게 생겼습니다:

```bash
echo >> ~/.zprofile
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**설치 확인하기:** 아래 명령어를 입력해 보세요:

```bash
brew --version
```

`Homebrew 4.x.x` 같은 버전 번호가 나오면 성공입니다.

### 4단계: DocVert에 필요한 프로그램 설치

```bash
brew install poppler tesseract libmagic
```

**화면에 나타나는 것:** 다운로드와 설치 진행 상황이 표시됩니다. 1~3분 정도 걸립니다.

> **이 프로그램들은 무엇인가요?**
>
> - `poppler` — PDF 파일에서 텍스트를 추출하는 프로그램
> - `tesseract` — 이미지 속 글자를 인식하는 프로그램 (OCR)
> - `libmagic` — 파일 종류를 자동으로 판별하는 프로그램

### 5단계: uv 설치

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**설치 후 반드시 해야 할 것:** 터미널 창을 **완전히 닫고**(빨간색 X 버튼) **새로 열어주세요**.

> **uv는 뭔가요?** DocVert가 필요로 하는 파이썬(Python) 환경을 자동으로 설치하고 관리해주는 도구입니다. 여러분이 파이썬을 직접 설치할 필요가 없습니다.

### 6단계: DocVert 다운로드

```bash
git clone https://github.com/seonghobae/docvert.git
```

**화면에 나타나는 것:**

```
Cloning into 'docvert'...
remote: Enumerating objects: ...
Receiving objects: 100% ...
```

이렇게 나오면 다운로드 성공입니다. 이제 다운로드한 폴더로 이동합니다:

```bash
cd docvert
```

> **`cd`는 뭔가요?** "이 폴더로 이동해라"는 뜻입니다. `cd docvert`는 방금 다운로드한 docvert 폴더 안으로 들어가는 명령어입니다.

그리고 필요한 라이브러리를 설치합니다:

```bash
uv sync
```

**화면에 나타나는 것:** 여러 라이브러리가 다운로드되는 과정이 표시됩니다. 처음에는 2~5분 걸릴 수 있습니다.

### 7단계: 설치 확인

```bash
uv run python -m docvert.cli.main --help
```

**성공하면 이렇게 나옵니다:**

```
usage: python3 -m docvert.cli.main [-h] [-V] {convert,batch} ...

Docvert: Convert documents to Markdown.

positional arguments:
  {convert,batch}
    convert        Convert a single DOCX or PDF file to Markdown.
    batch          Process a directory of DOCX and/or PDF files.
```

이런 도움말이 표시되면 설치 완료입니다!

**버전 확인하기:**

```bash
uv run python -m docvert.cli.main -V
```

`docvert 0.2.2` 같은 버전 번호가 나옵니다. [사용 방법](#사용-방법)으로 이동하세요.

---

## Windows 설치 안내

Windows에서는 먼저 **WSL**이라는 것을 설치합니다. WSL은 Windows 안에서 리눅스를 사용할 수 있게 해주는 공식 기능입니다.

### 1단계: WSL 설치

1. 화면 왼쪽 아래 **시작 버튼**을 클릭합니다.
2. `PowerShell` 이라고 입력합니다.
3. **"Windows PowerShell"** 이 나타나면, **마우스 오른쪽 클릭** → **"관리자 권한으로 실행"** 을 클릭합니다.
4. "이 앱이 변경을 할 수 있도록 허용하시겠습니까?" 라는 창이 뜨면 **"예"**를 클릭합니다.
5. 파란색 PowerShell 창이 열리면 아래를 붙여넣고 Enter를 누릅니다:

```cmd
wsl --install
```

6. 설치가 끝나면 **컴퓨터를 재부팅**합니다.

**재부팅 후:** 자동으로 Ubuntu라는 프로그램이 열리면서 사용자 이름과 비밀번호를 설정하라고 합니다.

- **사용자 이름:** 영문 소문자로 아무 이름이나 입력합니다 (예: `myname`)
- **비밀번호:** 아무 비밀번호나 설정합니다. **화면에 아무것도 안 보이는 게 정상입니다.** 그냥 입력하고 Enter를 누르세요. 한 번 더 같은 비밀번호를 입력합니다.

> **버전 요구사항:** Windows 10 (2004 이상) 또는 Windows 11이 필요합니다.
> 확인 방법: 시작 → 설정 → 시스템 → 정보 → "Windows 사양" 에서 버전 확인

### 2단계: 필수 프로그램 설치

Ubuntu 터미널(검은 창)에서 아래를 한 줄씩 실행합니다:

```bash
sudo apt update
```

1단계에서 설정한 비밀번호를 입력합니다 (화면에 안 보이는 게 정상).

```bash
sudo apt install -y poppler-utils tesseract-ocr libmagic-dev curl git
```

**화면에 나타나는 것:** 여러 프로그램이 다운로드되고 설치됩니다. 1~2분 걸립니다.

### 3단계: uv 설치

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치 후 아래를 실행합니다:

```bash
source $HOME/.local/bin/env
```

### 4단계: DocVert 다운로드

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

### 5단계: 설치 확인

```bash
uv run python -m docvert.cli.main --help
```

도움말이 표시되면 성공입니다! 버전도 확인해 보세요:

```bash
uv run python -m docvert.cli.main -V
```

[사용 방법](#사용-방법)으로 이동하세요.

### 참고: Windows 파일은 어디에 있나요?

WSL에서 Windows의 C드라이브에 접근하려면 `/mnt/c/` 를 사용합니다.

| Windows 경로 | WSL에서의 경로 |
|---|---|
| `C:\Users\홍길동\Desktop\` | `/mnt/c/Users/홍길동/Desktop/` |
| `C:\Users\홍길동\Documents\` | `/mnt/c/Users/홍길동/Documents/` |
| `D:\업무자료\` | `/mnt/d/업무자료/` |

> 사용자 이름을 모르면 Windows 탐색기에서 `C:\Users\` 폴더를 열어보세요.

---

## Linux 설치 안내

### Ubuntu / Debian

터미널을 열고 아래를 한 줄씩 실행합니다:

```bash
sudo apt update
sudo apt install -y poppler-utils tesseract-ocr libmagic-dev curl git
```

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

설치 확인:

```bash
uv run python -m docvert.cli.main --help
uv run python -m docvert.cli.main -V
```

### Fedora / RHEL / CentOS

```bash
sudo dnf install -y poppler-utils tesseract libmagic curl git
```

나머지는 Ubuntu와 동일합니다 (`curl ... uv` → `git clone ...` → `uv sync`).

---

## 폐쇄망 설치 안내

인터넷이 차단된 보안망에서 사용하는 방법입니다.

### 필요한 것

- 인터넷이 **되는** 컴퓨터 1대
- USB 메모리 (4GB 이상)
- 폐쇄망 컴퓨터에 **Docker** 또는 **Podman**이 설치되어 있어야 합니다

### 인터넷 되는 컴퓨터에서 준비

1. 웹브라우저에서 [https://github.com/seonghobae/docvert/releases](https://github.com/seonghobae/docvert/releases) 에 접속합니다.
2. 가장 위에 있는 최신 버전을 찾습니다.
3. `docvert-offline-release.tar.gz.part-aa`, `part-ab`, `part-ac` ... 라고 된 파일을 **전부** 다운로드합니다.
4. 다운로드한 파일들을 USB에 복사합니다.

### 폐쇄망 컴퓨터에서 설치

USB를 꽂고, 파일이 있는 위치에서 터미널을 열어 아래를 순서대로 실행합니다:

```bash
# 1. 분할 파일 합치기 (여러 개의 파일을 하나로 합칩니다)
cat docvert-offline-release.tar.gz.part-* > docvert-offline-release.tar.gz

# 2. 압축 풀기
tar -xzvf docvert-offline-release.tar.gz
cd docvert-offline-release

# 3. Docker에 설치
docker load -i docvert-offline.tar.gz
```

**설치 확인:**

```bash
docker images | grep docvert
```

`docvert` 라는 이름이 보이면 성공입니다!

### 폐쇄망에서 사용하기

```bash
# 현재 폴더의 PDF 파일을 변환
docker run --rm -v "$(pwd)":/data docvert:offline convert /data/파일이름.pdf --output-dir /data/결과

# 현재 폴더의 모든 문서를 변환
docker run --rm -v "$(pwd)":/data docvert:offline batch /data/문서폴더 --output-dir /data/결과
```

---

## 사용 방법

설치를 완료했으면 이제 문서를 변환할 수 있습니다.

### 기본 사용법: PDF 파일 하나 변환하기

**예시 상황:** 바탕화면에 `보고서.pdf` 파일이 있고, 이것을 마크다운으로 변환하고 싶습니다.

**Mac에서:**

```bash
# 1. 바탕화면으로 이동
cd ~/Desktop

# 2. 변환 실행
uv run python -m docvert.cli.main convert ./보고서.pdf --output-dir ./변환결과
```

**Windows(WSL)에서:**

```bash
# 1. 바탕화면으로 이동 ("홍길동"을 본인 사용자명으로 바꾸세요)
cd /mnt/c/Users/홍길동/Desktop

# 2. 변환 실행
uv run python -m docvert.cli.main convert ./보고서.pdf --output-dir ./변환결과
```

> **명령어 설명:**
>
> | 부분 | 의미 |
> |---|---|
> | `uv run python -m docvert.cli.main` | DocVert 프로그램을 실행합니다 |
> | `convert` | "하나의 파일을 변환해라" |
> | `./보고서.pdf` | 변환할 파일의 이름 |
> | `--output-dir ./변환결과` | 결과를 저장할 폴더 이름 (없으면 자동 생성됨) |

**성공하면 이렇게 나옵니다:**

```
Processing 1 files...
Processed 1 files. Failures: 0. Warnings: 0
```

### 워드(DOCX) 파일도 같은 방법으로

```bash
uv run python -m docvert.cli.main convert ./회의록.docx --output-dir ./변환결과
```

### 폴더 안의 모든 파일 한꺼번에 변환하기

**예시 상황:** `업무문서` 폴더 안에 PDF, DOCX 파일이 여러 개 있습니다.

```bash
uv run python -m docvert.cli.main batch ./업무문서 --output-dir ./변환결과
```

> `batch`는 폴더 안에 있는 **모든 PDF, DOCX 파일**을 자동으로 찾아서 변환합니다.
> 하위 폴더 안에 있는 파일도 전부 찾아줍니다.

### 변환 결과물 확인하기

변환이 완료되면 `변환결과` 폴더 안에 파일마다 3가지가 생깁니다:

```
변환결과/
├── 보고서.md              ← 변환된 텍스트 파일 (메모장으로 열 수 있음)
├── 보고서.conversion.json ← 변환 정보 (어떤 방식으로 변환했는지 기록)
└── 보고서.assets/         ← 문서에 있던 이미지 파일들
    ├── image_0.png
    └── image_1.png
```

**`.md` 파일 열어보기:**

- **Mac:** 파인더에서 더블클릭하면 텍스트 편집기로 열립니다.
- **Windows:** 메모장이나 VS Code로 열 수 있습니다.
- 또는 터미널에서: `cat 변환결과/보고서.md`

---

## 고급 옵션: 변환 세부 설정

DocVert는 문서 변환 방식을 세밀하게 조정할 수 있는 옵션을 제공합니다. 이 옵션들은 `convert`와 `batch` 모두에서 사용할 수 있습니다.

### 언어 및 OCR 설정

| 옵션 | 선택값 | 기본값 | 설명 |
|---|---|---|---|
| `--language-hint` | `ko`, `en`, `auto` | `auto` | 문서의 주요 언어를 지정합니다. |
| `--ocr-languages` | 공백으로 구분 | `ko en` | OCR에 사용할 언어 목록입니다. |

```bash
# 일본어+영어 OCR로 변환
uv run python -m docvert.cli.main convert ./doc.pdf --ocr-languages ja en
```

### 문서 요소 처리 방식

| 옵션 | 선택값 | 기본값 | 설명 |
|---|---|---|---|
| `--heading-mode` | `auto`, `style_only`, `heuristic` | `auto` | 제목 인식 전략 |
| `--comment-mode` | `preserve`, `appendix`, `inline`, `drop` | `preserve` | 주석(코멘트) 처리 방식 |
| `--footnote-mode` | `preserve`, `appendix`, `inline` | `preserve` | 각주 처리 방식 |
| `--image-mode` | `extract_link`, `embed`, `extract_with_ocr`, `skip` | `extract_link` | 이미지 처리 방식 |
| `--table-mode` | `markdown_preferred`, `html_for_complex` | `markdown_preferred` | 표 출력 형식 |
| `--pdf-reading-order-mode` | `auto`, `layout_strict`, `ocr_fallback` | `auto` | PDF 읽기 순서 전략 |

### 켜기/끄기 플래그

`--플래그` 로 켜고 `--no-플래그` 로 끕니다.

| 플래그 | 기본값 | 설명 |
|---|---|---|
| `--include-headers-footers` | 꺼짐 | 머리글/바닥글을 결과에 포함 |
| `--normalize-heading-levels` | 켜짐 | 제목 수준을 h1부터 시작하도록 정규화 |
| `--preserve-numbering` | 켜짐 | 목록과 제목의 번호 유지 |
| `--deterministic` | 켜짐 | 결정적 출력 (LLM 무작위 샘플링 비활성화) |
| `--aggressive-heading-inference` | 꺼짐 | 글꼴 크기, 굵기 등으로 제목을 적극 추론 |

```bash
# 이미지 OCR 추출 + 머리글/바닥글 포함 + 적극적 제목 추론
uv run python -m docvert.cli.main convert ./scan.pdf \
  --image-mode extract_with_ocr \
  --include-headers-footers \
  --aggressive-heading-inference
```

### batch 전용 옵션

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `--continue-on-error` / `--no-continue-on-error` | 켜짐 | 파일 하나가 실패해도 나머지를 계속 처리 |
| `--cache` | 꺼짐 | 해시 기반 캐시로 이미 처리한 파일 건너뛰기 |

---

## 고급 기능: AI로 결과 다듬기 (선택사항)

변환 결과를 AI가 한 번 더 깔끔하게 교정해줄 수 있습니다. 이 기능은 **선택사항**이며, 인터넷 연결이 필요합니다 (로컬 AI를 사용하면 인터넷 없이도 가능).

### AI 모델 선택하기

기본적으로 OpenAI의 `gpt-4o-mini` 모델을 사용합니다. `--llm-model` 옵션으로 다른 모델을 지정할 수 있습니다:

```bash
# 기본 모델 (gpt-4o-mini)
uv run python -m docvert.cli.main convert ./보고서.pdf --llm-refiner

# GPT-4o 사용
uv run python -m docvert.cli.main convert ./보고서.pdf --llm-refiner --llm-model gpt-4o

# Claude 사용
uv run python -m docvert.cli.main convert ./보고서.pdf --llm-refiner --llm-model claude-3-5-sonnet-20241022

# Ollama 로컬 모델 사용
uv run python -m docvert.cli.main convert ./보고서.pdf --llm-refiner --llm-model llama3
```

### 방법 1: OpenAI 사용 (유료)

1. [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys) 에서 API 키를 발급받습니다.
2. 아래처럼 사용합니다:

```bash
export OPENAI_API_KEY="sk-여기에-발급받은-키를-붙여넣으세요"
uv run python -m docvert.cli.main convert ./보고서.pdf --output-dir ./결과 --llm-refiner
```

> `--llm-refiner`를 붙이면 AI 교정이 켜집니다.

### 방법 2: Ollama 사용 (무료, 인터넷 불필요)

[Ollama](https://ollama.com/) 는 내 컴퓨터에서 AI를 돌릴 수 있게 해주는 프로그램입니다.

```bash
# Ollama 설치 후 (https://ollama.com 에서 다운로드)
ollama pull llama3

# 환경 설정
export OPENAI_API_KEY="dummy"
export OPENAI_BASE_URL="http://localhost:11434/v1"

# AI 교정 켜고 변환
uv run python -m docvert.cli.main convert ./보고서.pdf --output-dir ./결과 --llm-refiner --llm-model llama3
```

---

## 문제가 생겼을 때

### "command not found: uv"

터미널을 완전히 닫고 다시 열어보세요. 그래도 안 되면:

```bash
source $HOME/.local/bin/env
```

### "command not found: git"

git이 설치되지 않은 상태입니다.

- **Mac:** 2단계(개발 도구 설치)를 다시 실행하세요.
- **Ubuntu/Debian:** `sudo apt install -y git`
- **Fedora/RHEL:** `sudo dnf install -y git`

### "pdfinfo not found"

PDF 관련 프로그램이 설치되지 않았습니다.

- **Mac:** `brew install poppler`
- **Ubuntu/Debian:** `sudo apt install -y poppler-utils`
- **Fedora/RHEL:** `sudo dnf install -y poppler-utils`

### "tesseract is not installed"

글자 인식(OCR) 프로그램이 설치되지 않았습니다.

- **Mac:** `brew install tesseract`
- **Ubuntu/Debian:** `sudo apt install -y tesseract-ocr`
- **Fedora/RHEL:** `sudo dnf install -y tesseract`

### 파이썬을 따로 설치해야 하나요?

아닙니다. `uv`가 자동으로 설치합니다. 별도로 할 일 없습니다.

### 변환 결과의 품질이 아쉬워요

`--llm-refiner` 옵션으로 AI 교정을 켜보세요. [AI로 결과 다듬기](#고급-기능-ai로-결과-다듬기-선택사항)를 참고하세요.

### DocVert를 최신 버전으로 업데이트하고 싶어요

DocVert를 다운로드했던 폴더에서:

```bash
cd docvert
git pull
uv sync
```

### "cd docvert" 했는데 "No such file or directory" 라고 나와요

DocVert가 다운로드된 위치가 다릅니다. 보통 홈 폴더에 있습니다:

```bash
cd ~/docvert
```

그래도 안 되면 DocVert를 다시 다운로드하세요 (6단계부터).
