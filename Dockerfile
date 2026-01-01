FROM python:3.12-bookworm

WORKDIR /app

# Сначала устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Создаем директорию для данных
RUN mkdir -p /app/data

# Копируем остальной код
COPY . .

# Указываем volume
VOLUME [ "/app/data" ]

# Команда запуска
CMD ["python", "main.py"]