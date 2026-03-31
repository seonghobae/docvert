FROM python:3.14-rc-slim

# Install system dependencies required for unstructured and pdf rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy the project files
COPY pyproject.toml README.md uv.lock ./
COPY docvert/ ./docvert/
COPY main.py ./main.py

# Install dependencies and the project itself using uv
RUN uv pip install --system .

# Set entrypoint to use the CLI
ENTRYPOINT ["docvert"]
CMD ["--help"]
