FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ---- system dependencies for your libs ----
# - libgl1, libglib2.0-0: pymupdf (fitz)
# - libmagic1: unstructured filetype detection
# - poppler-utils: PDF text extraction (optional but common)
# - curl/ca-certificates: general networking sanity
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libmagic1 \
    poppler-utils \
    curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Copy and install python package (uses poetry-core backend)
COPY pyproject.toml README.md /app/
# if you have a src layout (you do), copy src/ and app.py
COPY src/ /app/src/
COPY static/ /app/static/
COPY templates/ /app/templates/
COPY app.py /app/
# (if you have other runtime files, copy them too)
# COPY templates/ static/ ...

# Install your project (builds wheel via poetry-core and installs)
RUN pip install --no-cache-dir .

# Expose Flask/Gunicorn port
EXPOSE 5050

ENV FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0


CMD ["gunicorn", "-k", "eventlet", "-w", "1", "--timeout", "0", "-b", "0.0.0.0:5050", "app:app"]
