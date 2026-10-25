# Варіант 1: Енергоощадна розумна квартира

**Відеодемонстрація:** [Посилання на YouTube / Google Drive]

## Опис системи
Проєкт реалізує комплексну IoT-систему для розумного будинку на базі Python-симуляторів, брокера Mosquitto (MQTT) з підтримкою TLS та системи openHAB.

## Швидкий запуск
1. Генерація сертифікатів:
   ```bash
   ./certs/generate.sh
docker compose up -d
graph TD
    subgraph Рівень сприйняття
        S1[Датчик руху/світла] -->|telemetry| M
        A1[Диммер / Обігрівач] <--set/state--> M
    end
    subgraph Мережевий рівень
        M[Mosquitto TLS 8883 + ACL]
    end
    subgraph Рівень обробки
        O[openHAB Engine / Rules] <-->|MQTT binding| M
    end
    subgraph Рівень застосунків
        UI[MainUI / Sitemap / Графік] <--> O
    end
