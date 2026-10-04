FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential cmake && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
# put dure-reader-q8_0.gguf (531 MB, built by ai/coffee: convert merged/ with llama.cpp's convert_hf_to_gguf.py --outtype q8_0) next to app.py
COPY dure-reader-q8_0.gguf .
ENV MODEL_ID=./dure-reader-q8_0.gguf
EXPOSE 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
