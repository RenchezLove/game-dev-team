# Заметки: два слота огнестрела и кнопка ножа (10.10.2026)

Копия `E:/ContrarySurvior/ws-weapons`, ветка `feature/weapon-slots-1010`, коммит `3b4307a` поверх `410e042`, на сервер не отправлен. Сборка редакторной цели без ошибок (`logs/build_weapon_slots_final.log`), проверки 232 из 232 (`logs/tests_weapon_slots_full.log`). Игровая цель (телефон) НЕ собиралась.

## Устройство
- Слот — признак ствола: `ARangedWeapon::FirearmSlot` (`EFirearmSlot::Sidearm` / `Long`), у `AShotgun` — `Long`.
- Игрок: `SidearmWeaponInstance`, `LongWeaponInstance`, `PreferredFirearmSlot` (последний ствол в руках). Доступ: `GetFirearmInSlot`, `IsSlotFirearm`, `GetEquippedFirearmCount`, `SelectFirearmSlot`, `TakeKnifeInHands`, `UnequipFirearmToBackpack`. `GetRangedWeaponInstance()` оставлен как «ствол в руках, иначе тот, что возьмёт кнопка смены» — старые экранные проверки рассинхрона на нём работают без правок.
- `TryAdoptRangedWeapon` / `SwapRangedWeaponFromBackpack` работают со слотом вида этого ствола.
- Нож с кнопки: `APlayerCharacter::QuickMeleeAttack` → `AMeleeWeapon::StartSwing` (тот же удар). Метка анимации берёт нож через `AMasterHumanoidCharacter::GetSwingMeleeWeapon` (у игрока — всегда его нож). На время `QuickMeleeLockTime` (0,6 с) ствол спрятан, нож прикреплён к ладони (`AttachWeaponToHand`, вынесено из `EquipWeapon`), `FireCurrentWeapon` игрока не стреляет.
- Сохранение: по записи с `bEquipped` на каждый занятый слот, поле `UContrarySaveGame::WeaponInHands` (`Unknown` у старых записей — руки не трогаются).
- Перезарядка в проекте мгновенная (таймера нет), поэтому вопрос «замах и перезарядка» не возникает.

## Готовые файлы окон
- Добавлено дополнением: `MeleeButton` + `MeleeButtonIcon` в `WBP_TouchControls`; `LongSlotButton` (внутри подпись, значок, название) и `RangedSlotButton` в `WBP_Inventory`. Функции `AugmentTouchMeleeButton`, `AugmentInventoryWeaponSlots`.
- Раскладка сумки у Рината своя: средняя колонка занята пистолетом и ножом, третий слот встал под слотом штанов. Наивное «ниже ножа с тем же шагом» вылезало за подложку — сначала смотреть снимок раскладки, потом ставить.
- Проверка окон (`-verify`) на базовом снимке уже красная (14 старых замечаний к файлам Рината); доказательство — одинаковый список до и после.
- Двоичные файлы окон между ветками не сливаются: после слияния взять любую версию и прогнать дополнение ещё раз.

## Не сделано
- Клавиши 1 и 2 заняты отладочными действиями Рината (деньги и снимок экрана) — прямой выбор слота с клавиатуры не привязан, функция `SelectFirearmSlot` есть.
- Подсветка сектора удара показывается только с ножом в руках (как раньше), при ударе с кнопки её нет.
- Модель длинного оружия за спиной — не просили.
