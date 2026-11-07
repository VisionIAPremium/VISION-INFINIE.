FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VISION_INFINIE_HOST=0.0.0.0 \
    VISION_INFINIE_PORT=8765

WORKDIR /app
COPY --chown=10001:10001 . /app
RUN groupadd --system --gid 10001 vision \
    && useradd --system --uid 10001 --gid vision --home-dir /app vision \
    && mkdir -p /app/data/memory /app/data/audit \
    && chown -R vision:vision /app
USER 10001:10001

EXPOSE 8765
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8765/health', timeout=3)"
CMD ["python", "app.py"]
