
## 2026-07-18 — интеграционный гейт двух веток (закрыто)
- `feature/ui-bp-and-shop-scroll` (97b416b) + `fix/android-storage-and-cloth` (79ca38b) слиты в локальную `qa/integration-gate-2026-07-18` без конфликтов; сборка -NoUBA exit 0, тесты 16/16; дефолты сверены дословно; дано добро на merge. Логи: `context/qa/logs/build-2026-07-18-qa-integration-gate*.log`, `tests-2026-07-18-qa-integration-gate.log`.

## 2026-08-01 — мерж-гейт Build 1.2 feature/build12-night (закрыто, слито)
- HEAD `50ab6a6` против master `f9ee6c8`: ГОДНО по всем 5 пунктам (Rebuild чистый, тесты 26/26, verify wbp/animbp/gripsocket, дифф 63 файла без мусора/ключей, LFS полный). Логи: `context/qa/logs/*-2026-08-01-b12-*.log`.

## 2026-08-02 — мерж-гейт feature/build121-fixes (закрыт)
ГОДНО по всем 5 пунктам ТЗ Build 1.2.1 (HEAD 188b5fd). Пруфы в context/qa/logs/ с префиксом b121-gate: rebuild (обе DLL, EXIT=0), tests (32/32 Success), wbp-verify (12 WBP OK), dumpslots, diff-stat/diff-text (58 файлов, hex-секретов 0), lfs (17/17). Дальше шла живая приёмка Рината.
