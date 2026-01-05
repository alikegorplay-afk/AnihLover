#!/bin/bash

set -e

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

# Основной процесс
main() {
    log "Начало обновления приложения"
    
    # Git pull
    log "Выполняем git pull..."
    if ! git pull; then
        error "Не удалось получить обновления из Git"
    fi
    
    # Проверяем изменения в зависимостях
    if git diff HEAD@{1} -- package.json docker-compose.yml | grep -q "^[+-]"; then
        log "Обнаружены изменения в конфигурационных файлах"
    fi
    
    # Останавливаем
    log "Останавливаем старые контейнеры..."
    docker-compose down
    
    # Собираем с очисткой кэша при необходимости
    log "Собираем образы..."
    docker-compose build --pull --no-cache
    
    # Запускаем
    log "Запускаем контейнеры..."
    docker-compose up -d
    
    # Ждём запуска и проверяем здоровье
    log "Ожидаем запуска сервисов..."
    sleep 10
    
    # Проверяем, что контейнеры запущены
    if ! docker-compose ps | grep -q "Up"; then
        error "Контейнеры не запустились"
    fi
    
    log "Приложение успешно обновлено и запущено!"
    log "Используйте 'docker-compose logs -f' для просмотра логов"
}

# Запуск
main "$@"