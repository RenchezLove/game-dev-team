
## 2026-07-18 — интеграционный гейт двух веток (закрыто)
- `feature/ui-bp-and-shop-scroll` (97b416b) + `fix/android-storage-and-cloth` (79ca38b) слиты в локальную `qa/integration-gate-2026-07-18` без конфликтов; сборка -NoUBA exit 0, тесты 16/16; дефолты сверены дословно; дано добро на merge. Логи: `context/qa/logs/build-2026-07-18-qa-integration-gate*.log`, `tests-2026-07-18-qa-integration-gate.log`.

## 2026-08-01 — мерж-гейт Build 1.2 feature/build12-night (закрыто, слито)
- HEAD `50ab6a6` против master `f9ee6c8`: ГОДНО по всем 5 пунктам (Rebuild чистый, тесты 26/26, verify wbp/animbp/gripsocket, дифф 63 файла без мусора/ключей, LFS полный). Логи: `context/qa/logs/*-2026-08-01-b12-*.log`.

## 2026-08-02 — мерж-гейт feature/build121-fixes (закрыт)
ГОДНО по всем 5 пунктам ТЗ Build 1.2.1 (HEAD 188b5fd). Пруфы в context/qa/logs/ с префиксом b121-gate: rebuild (обе DLL, EXIT=0), tests (32/32 Success), wbp-verify (12 WBP OK), dumpslots, diff-stat/diff-text (58 файлов, hex-секретов 0), lfs (17/17). Дальше шла живая приёмка Рината.

## 2026-08-08 мерж-гейт feature/night-0807 (ЗАКРЫТ, влит в 0ec0a43)
ДОБРО дано, вердикт финальный. Гейт волны (7 коммитов до 0181111): qa-gate2-build.log — реальная компиляция после touch 21 .cpp, линк обеих DLL, 0 ошибок; qa-gate2-tests.log — 81/81 (ветка 81, master 74); qa-gate2-wbp.log — 19 WBP VERIFY OK. Дельта 0ec0a43 (индикатор хромоты): дифф чистый, qa-gate2-tests-delta.log 81/0 EXIT 0. Дифф/LFS/секреты чистые.

## Мерж-гейт 2026-08-08 `fix/shop-pause-bones-0808` — ДОБРО (закрыт, смёржен)
- 2026-08-08 мерж-гейт `fix/shop-pause-bones-0808` (4 коммита d7291fb..963b1a6 поверх master 0ec0a43): **ДОБРО НА МЕРЖ** — вердикт отдан game-lead. Прошлый гейт night-0807 вынесен в archive.md.
- Сборка (`Saved/qa-gate3-build.log`): touch 4 правленых .cpp + новый тест, реальная компиляция `Module.ContrarySurvivor.10/12.cpp`, линк .lib и .dll, DLL перелинкована 10:58:54 (была 10:49:12), 0 ошибок, exit 0.
- Тесты (`Saved/qa-gate3-tests.log`): 82 Success / 0 Fail (макросов ветка 82, master 81 = +1 новый ShopBackpackWeapon), TEST COMPLETE EXIT CODE 0, GIsCriticalError=0. Регрессии оружия зелёные: StartWithoutFirearm, WeaponSlotDesync.*(3), WeaponUiGating.RangedGate; новый PurchasedFirearmGoesToBackpackThenTapEquips=Success.
- Логика проверена глазами: TryAdoptRangedWeapon при не-огнестреле/занятом слоте возвращает false, предмет остаётся в рюкзаке (ветка HandleTileUse для любой категории Weapon безопасна, потерь/дублей нет). Пауза: убрано только согласие, строка политики и номер версии сохранены (RefreshConsentAndVersion цел). L_World_C.umap — LFS-указатель. Дифф/секреты чистые (позитивный контроль сработал).
- Следующий шаг: за game-lead — маркер QA_OK и merge в master. Дерево чистое, HEAD d7291fb, замок сборки снят.
