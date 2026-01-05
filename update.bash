#!/bin/bash

# Устанавливаем полное окружение
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export HOME=/root
cd /root/AnihLover || exit 1

# Лог файл для отладки
LOG_FILE="/root/AnihLover/update.log"

exec > >(tee -a "$LOG_FILE") 2>&1

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ОШИБКА: $1${NC}"
    exit 1
}

# Проверка наличия команд
check_commands() {
    command -v docker >/dev/null 2>&1 || error "docker не найден"
    command -v docker-compose >/dev/null 2>&1 || command -v docker compose >/dev/null 2>&1 || error "docker-compose не найден"
}

# Основной процесс
main() {
    log "Начало обновления приложения"
    
    # Проверяем команды
    check_commands
    
    # Используем правильную команду docker-compose
    if command -v docker-compose >/dev/null 2>&1; then
        DC_CMD="docker-compose"
    else
        DC_CMD="docker compose"
    fi

    # Git pull
    log "Выполняем git pull..."
    if ! git pull; then
        error "Не удалось получить обновления из Git"
    fi

    # Сохраняем старые версии файлов для сравнения
    OLD_PACKAGE=$(md5sum package.json 2>/dev/null || echo "")
    OLD_DOCKER=$(md5sum docker-compose.yml 2>/dev/null || echo "")

    # Останавливаем
    log "Останавливаем старые контейнеры..."
    $DC_CMD down

    # Собираем с очисткой кэша при необходимости
    log "Собираем образы..."
    $DC_CMD build --pull

    # Запускаем
    log "Запускаем контейнеры..."
    $DC_CMD up -d

    # Ждём запуска и проверяем здоровье
    log "Ожидаем запуска сервисов..."
    sleep 10

    # Проверяем, что контейнеры запущены
    if ! $DC_CMD ps | grep -q "Up"; then
        error "Контейнеры не запустились"
    fi

    log "Приложение успешно обновлено и запущено!"
    log "Лог сохранен в: $LOG_FILE"
}

# Запуск
main "$@"