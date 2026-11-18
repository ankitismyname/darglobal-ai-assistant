# DarGlobal & Wasalt Property Assistant
# Build:  docker build -t property-assistant .
# Run:    docker run -p 7860:7860 -e OPENROUTER_API_KEY=sk-or-... property-assistant
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    GRADIO_ANALYTICS_ENABLED=False \
    HF_HUB_DISABLE_TELEMETRY=1 \
    HOME=/home/user \
    PORT=7860

# Hugging Face Spaces runs containers as uid 1000
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

COPY --chown=user requirements.txt .
RUN pip install -r requirements.txt

USER user
COPY --chown=user app/ app/
COPY --chown=user data/raw/ data/raw/

# Download the embedding model and build the search index at build time, so the container starts in seconds
# and the image is reproducible from the raw scraped data alone.
RUN python app/build_index.py

EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860/health', timeout=4)" || exit 1

CMD ["python", "app/main.py"]
