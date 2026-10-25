#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=== Генерація CA та сертифікатів TLS ==="
# 1. Створення власних CA (Certificate Authority)
openssl req -new -x509 -days 365 -nodes -out ca.crt -keyout ca.key \
    -subj "/C=UA/ST=Sumy/L=Buryn/O=IoT-Lab/CN=SmartFlatCA"

# 2. Сертифікат сервера Mosquitto
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
    -subj "/C=UA/ST=Sumy/L=Buryn/O=IoT-Lab/CN=mosquitto"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365

# Права доступу для приватних ключів
chmod 600 ca.key server.key

echo "=== Сертифікати успішно згенеровано ==="
