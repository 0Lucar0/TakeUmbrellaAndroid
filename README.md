# Take Umbrella (Возьми зонтик)

Android-приложение на Python (Kivy + plyer + pyjnius).

Идея: каждое утро проверять прогноз на сегодня в городе пользователя и присылать уведомление:
`"Возьми зонтик! Сегодня ожидается дождь (60%)"` при вероятности осадков >= порога.

## Стек
- UI: Kivy (+ `.kv`)
- Погода: Open‑Meteo (без ключа)
- Геокодинг (поиск города): Open‑Meteo Geocoding (без ключа)
- Хранение: JSON в `App.user_data_dir`
- Уведомления: plyer.notification (и Android-обвязка через pyjnius при сборке)
- Планировщик: AlarmManager (Android) / fallback на `Clock` (dev)

## Структура
- `main.py` — точка входа (App)
- `umbrella/` — приложение (экраны + сервисы)
- `kv/` — разметка Kivy
- `service/` — фоновой сервис (Android): ежедневная проверка + уведомление
- `buildozer.spec` — сборка Android

## Запуск (desktop/dev)
```bash
python main.py
```

## Сборка Android (в Linux/WSL)
Buildozer требует Linux. В Windows обычно собирают через WSL2 или CI.

```bash
buildozer android debug
```

