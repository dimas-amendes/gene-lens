# Gene Lens — Docker image for the local web dashboard.
#
# This image is intentionally a development/single-user runner. It is NOT a
# production deployment target: the privacy posture (everything on your
# machine, no network during analysis) assumes the container also runs on
# your machine and that you mount your DNA file as a volume.
#
# Usage:
#   docker build -t gene-lens .
#   docker run --rm -p 5000:5000 \
#     -v "$PWD/data:/app/data" \
#     -v "$PWD/input:/app/input" \
#     -v "$PWD/output:/app/output" \
#     -v "$PWD/history:/app/history" \
#     gene-lens
#
# Then open http://127.0.0.1:5000.
#
# Reference databases (ClinVar, PharmGKB) live in the mounted data/ volume
# so they persist across container restarts. Use
#   docker run --rm -v "$PWD/data:/app/data" gene-lens python download_databases.py
# once to populate them.

FROM python:3.12-slim

# Avoid writing .pyc files and buffering stdout — both are dead weight in a
# container and the unbuffered output makes `docker logs` actually useful.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps: only what Python wheels actually need. Keep this list minimal
# so the image stays small; add packages here if a future dependency requires
# them at build time.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first for layer caching — code changes won't bust the
# pip install layer unless requirements.txt itself changes.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the project. .dockerignore keeps personal data and
# build artifacts out of the image.
COPY . .

# Pre-create the runtime directories that get bind-mounted at runtime so the
# app's ensure_directories() never fails before the volume is available.
RUN mkdir -p /app/data /app/input /app/output /app/history

EXPOSE 5000

# Bind to all interfaces inside the container so the host port mapping
# (-p 5000:5000) reaches the Flask server. The privacy guarantee that
# Flask only listens on 127.0.0.1 is enforced by docker's port mapping,
# not by the inner bind address.
ENV FLASK_APP=dashboard.py \
    PYTHONPATH=/app

CMD ["python", "-c", "from dashboard import run_dashboard; run_dashboard(port=5000)"]
