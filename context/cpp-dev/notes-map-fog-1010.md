# Заметки: карта КПК открывается по мере исследования (10.10.2026, вечер)

Копия `E:/ContrarySurvior/ws-weapons`, ветка `feature/inventory-slot-1010`, коммит `4bed730` (поверх `59f3e3a` и `cb1860a`), на сервер не отправлен. Сборка редакторной цели без ошибок (`logs/build_mapfog_1010_c.log`), проверки 247 из 247 (`logs/tests_mapfog_1010_full.log`), двенадцать проверок КПК отдельно прошли с настоящей отрисовкой (`logs/tests_mapfog_1010_render.log`). Игровая цель (телефон) НЕ собиралась. Живьём в игре не смотрел никто.

## Устройство
- `UI/PdaMapFog.h` — `FPdaMapFog`: сетка клеток в долях карты, `RevealCircle`, `Pack`/`Unpack` (длины серий), `ResampleTo`, `BuildAlpha` (маска с размытым краем). Чистые правила без мира.
- `Components/MapExplorationComponent` — память героя (`APlayerCharacter::GetMapExploration`): тик раз в `MapRevealInterval`, `ResetToVillage`, `RevealAroundOwner`, `RevealAll`, `IsWorldLocationRevealed`, счётчик изменений `GetRevision`, `WriteToSave`/`RestoreFromSave`.
- Сохранение: `UContrarySaveGame::MapFogWidth`, `MapFogHeight`, `MapFogRuns`. Читается в `BeginPlay` героя и в `LoadGameForContinue` (после переноса героя), пишется в `SaveGame`, сбрасывается в `ResetToNewGame`.
- Окно: `UPdaScreenWidget::UpdateFogMask` (картинка-маска `FogTexture`, элемент `MapFogImage`), места собираются в `RebuildMap` (объекты уровня, потом список настроек со слиянием по `MapPlaceMergeRadius`), `ClampArrowCenter`. Перерисовка — по счётчику изменений, не каждый кадр.
- Настройки: `UContraryPdaSettings`, раздел «Карта: исследование».
- Меню отладки: `ContraryDebugTools::RevealWholeMap`, `HideMapAgain`.
- В `WBP_Pda` элемент `MapFogImage` добавлен дополнением (`AugmentPdaMapFog`).

## Факты
- Камера героя (снято с `BP_PlayerCharacter`, `logs/camera_dump_mapfog_1010.txt`): штанга 3000, наклон 60° вниз, угол обзора 40°. Движок по умолчанию держит постоянным ВЕРТИКАЛЬНЫЙ угол (`AspectRatio_MaintainYFOV`, `BaseEngine.ini:2820`; пересчёт — `CameraStackTypes.cpp:326-333`), поэтому на широком экране видно шире, а не ниже.
- В служебном запуске без отрисовки (`-nullrhi`) картинка-маска не создаётся (`FApp::CanEverRender`), проверки смотрят байты маски. С ключом `-RenderOffscreen` путь картинки исполняется.
- Подпись «База учёных» теперь берётся из списка мест настроек (8700, −16000), а не с охранника у входа; поле окна `ScientistBaseLabel` удалено.

## Не сделано и не проверено
- Вид черноты и подписей в игре, плавность края, скорость на телефоне.
- Если углы карты в настройках поменяют после того, как игрок сохранился, открытое в его сохранении сдвинется относительно картинки (сетка хранится в долях карты).
- На карте без картинки линии сетки рисуются поверх черноты.
