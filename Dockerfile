FROM python:3.6-slim

WORKDIR /app

# System dependencies for C extensions (pyfastx)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    zlib1g-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --use-deprecated=legacy-resolver -r requirements.txt

# Copy application code
# - db/*_sample.db are included (~57 MB total)
# - transcript_sequences/ and full db/*.db are excluded via .dockerignore
COPY . .

# Make inDelphi importable
ENV PYTHONPATH=/app/Indelphi_installation/inDelphi-model-master

EXPOSE 8050

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
