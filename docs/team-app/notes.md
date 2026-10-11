# Программа «Моя команда разработки» — заметки

Схемы: `dashboard_home.png`, `dashboard_tasks.png`, `dashboard_docs.png`, `dashboard_assets.png` (исходник `dashboard.html`, картинки снимаются Edge без окна).

## Пожелания Рината (11.10.2026)
- После отправки задачи на главной раскрывается чат с руководителем команды, четыре блока («ждёт вашего решения», «сейчас в работе», «сделано сегодня», «ближайшие задачи») уезжают ниже.
- Картинки в чат — перетаскиванием и Ctrl+V.
- У каждой нейросети свой счётчик: лимит со сбросом / остаток денег / кредиты / бесплатно.

## Проверено по официальной документации 11.10.2026 (code.claude.com/docs)
- `headless.md`: запуск `claude -p` без ключа `--bare` загружает то же, что обычная сессия: правила проекта, перехватчики, специалистов, подключённые серверы. Вывод потоком — `--output-format stream-json`. Команды, работающие только в окне терминала (например `/login`), недоступны.
- `headless.md`: «bare mode doesn't use your subscription login» — то есть обычный режим `-p` работает под входом по подписке (вывод из формулировки, отдельно не испытано).
- `agent-sdk/overview.md`: «Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products, including agents built on the Claude Agent SDK» — раздавать программу другим людям с входом по подписке нельзя; для чужих пользователей — только ключ с оплатой по расходу.
- `statusline.md`: Claude Code передаёт скрипту строки состояния поля `rate_limits.five_hour.used_percentage`, `rate_limits.seven_day.used_percentage` и `resets_at` — проценты пятичасового и недельного лимита и время сброса. Приходят ли они при запуске без окна — НЕ ПРОВЕРЕНО.
- `agent-sdk/streaming-vs-single-mode.md`: в потоковом режиме к сообщению можно прикладывать картинки (блок `image`, base64).
