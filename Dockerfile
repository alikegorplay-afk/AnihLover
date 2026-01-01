FROM python:3.14.2-bookworm

WORKDIR /app

COPY requirements.txt .

# Установка FFmpeg через apt
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

RUN mkdir data
VOLUME [ "/app/data" ]

COPY . .

CMD ["python", "main.py"]