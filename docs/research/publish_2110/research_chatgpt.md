Ниже — **практическая картина на 22 октября 2026 г.** Это не юрзаключение; по валютному контролю и структуре выплат лучше отдельно проверить у налогового/валютного юриста, потому что цена ошибки — блокировка аккаунта или штраф.

## Короткий вывод

| Направление | Самый реалистичный путь для описанного разработчика |
|---|---|
| **Steam** | **Можно пробовать как физлицо/sole proprietor из РФ**, но только с **реальным банковским счётом на своё имя**, способным принять USD SWIFT. Сингапурская *карта* не подходит; сингапурский *банковский счёт на имя разработчика* может подойти, если Valve/TaxIdentity пропустят KYC. Монетизация — продажи/DLC/Steam IAP, **не реклама**. |
| **Google Play** | **Бесплатная публикация из РФ — да. Монетизация через Google Play Billing — практически нет**, если нет иностранного юрлица/платёжного профиля: для российских disbursement bank accounts seller services приостановлены, а российские пользователи всё равно не могут покупать paid/IAP. Рабочий вариант — free app + сторонняя реклама, лучше Яндекс/VK для RU-аудитории. |
| **App Store** | **Регистрация из РФ вероятно возможна**, но нужна оплата $99 не российской картой и прохождение identity/compliance. Монетизация через Apple работает в основном **на нероссийскую аудиторию**: с 1 апреля 2026 покупки/IAP в России почти недоступны. Выплаты — на банковский счёт на имя разработчика; карта/посредник без счёта не годится. |
| **Реклама** | **AdMob для Russia-based publisher — нет**. Самый реалистичный рекламный доход из РФ — **Яндекс Рекламная сеть как самозанятый**, плюс VK/другие сети через медиацию. AppLovin/Unity — теоретически, но по РФ/KYC/платежам нужно индивидуально проверять в кабинете и у поддержки. |
| **Лучший общий маршрут** | 1) Steam — самопубликация как физлицо, если есть нормальный иностранный счёт. 2) Google Play/App Store — free-to-play + Яндекс/VK Ads для RU, IAP/продажи — только через иностранную структуру или издателя. 3) Если цель — полноценные IAP/продажи на mobile globally, открывать зарубежное ИП/юрлицо или идти к издателю. |

---

# 1. Steam

## 1.1. Можно ли гражданину/резиденту РФ зарегистрироваться

**Проверено по официальным правилам Steamworks.** У Valve нет найденного мной общего запрета “Russia-based developers cannot register”. В FAQ Valve прямо указывает запрет на работу с лицами/организациями под санкциями OFAC/SDN/FSE и с embargoed regions/countries, среди которых названы Crimea, Cuba, Iran, North Korea; Россия как страна целиком в этом списке не указана. Но Valve не будет работать с санкционным лицом/организацией или с лицом из запрещённого региона. ([partner.steamgames.com](https://partner.steamgames.com/doc/gettingstarted/faq))

Для онбординга Steamworks нужно: подписать цифровые документы, оплатить **$100 app fee** за продукт, заполнить банковскую и налоговую информацию, пройти identity verification. Steam прямо пишет, что можно онбордиться как individual/sole proprietor, но имя в банковском счёте должно совпадать с Legal Company Name/юридическим именем. ([partner.steamgames.com](https://partner.steamgames.com/doc/gettingstarted/onboarding?language=english))

По налогам Steam проводит tax interview; для non‑US обычно используется W‑8BEN/W‑8BEN‑E. Valve указывает, что налоговая проверка идёт через сторонний сервис TaxIdentity/Lilaham, может занять 2–7 рабочих дней по FAQ, а в onboarding-документации также предупреждает о возможных сроках до 30 дней и запросе дополнительных документов. ([partner.steamgames.com](https://partner.steamgames.com/doc/gettingstarted/faq))

**Что именно блокирует:**  
1) санкционный статус самого разработчика/банка/региона;  
2) несовпадение имени в Steamworks, налоговой форме и банке;  
3) отсутствие валидного банковского счёта;  
4) невозможность пройти TaxIdentity/KYC;  
5) контентные ограничения. Важно: Steam прямо относит к тому, что не следует публиковать, **“applications with advertising-based business models”** — то есть модель “бесплатная ПК-игра с рекламой” для Steam плохая идея. ([partner.steamgames.com](https://partner.steamgames.com/doc/gettingstarted/onboarding?language=english))

## 1.2. Как Steam выплачивает деньги и что с сингапурской картой

Steam платит при достижении порога **$100**, за предыдущий месяц, обычно в конце следующего месяца. Для банков вне США Valve отправляет **USD SWIFT wires**. ([partner.steamgames.com](https://partner.steamgames.com/doc/finance/payments_salesreporting))

**Карта Сингапура через “Платипо всему миру” сама по себе не подходит**: Steam просит банковскую информацию — routing/account/bank address/SWIFT, а не номер карты. Если у разработчика есть именно **банковский счёт/платёжный счёт в Сингапуре на его полное юридическое имя**, с реквизитами для входящих wire/SWIFT, теоретически его можно пробовать указать. Но если это “карта посредника”, pooled account, FBO/FFC-схема или счёт не на имя разработчика — высок риск отказа из-за несовпадения account holder name. Steam прямо требует совпадения имени владельца банковского счёта с именем, указанным при онбординге. ([partner.steamgames.com](https://partner.steamgames.com/doc/gettingstarted/onboarding?language=english))

## 1.3. Самозанятость и налоги для Steam

**Собственный вывод, не индивидуальная налоговая консультация.** Доход от Steam для российского физлица обычно можно квалифицировать как доход от использования/реализации прав на собственный цифровой продукт или как royalty/revenue share. Valve в своей налоговой документации классифицирует revenue share payments как royalty для целей американской отчётности. ([partner.steamgames.com](https://partner.steamgames.com/doc/finance/taxfaq?l=english&language=english))

Для НПД ключевые практические условия: доход самозанятого — до **2,4 млн руб. в год**, без наёмных сотрудников; при работе с юрлицами ставка обычно **6%**. Яндекс в своём разделе для самозанятых также указывает лимит 2,4 млн руб. и ставку 6% при выплатах от юрлица. ([yandex.ru](https://yandex.ru/project/yan/npd?utm_source=openai))

Если Steam/Valve платит как иностранная компания, для НПД это, как правило, доход от юрлица/организации → **6%**. В “Мой налог” лучше формировать чек на сумму фактического поступления в рублёвом эквиваленте по курсу ЦБ на дату получения, но схему чеков по иностранным платформам лучше подтвердить у бухгалтера: договоры Steam, Apple и Google отличаются — где-то платформа агент/комиссионер, где-то royalty/revenue share.

Если деньги идут на зарубежный счёт, для резидента РФ включается валютное регулирование: нужно уведомлять ФНС об открытии/закрытии/изменении реквизитов зарубежных счетов и, в ряде случаев, сдавать отчёт о движении средств. ФНС указывает пороговое исключение по отчёту при суммах/остатках до эквивалента **600 000 руб.**, но это зависит от условий и страны/типа счёта; по общему правилу отчёт физлица подаётся ежегодно до 1 июня года, следующего за отчётным. ([nalog.gov.ru](https://www.nalog.gov.ru/rn77/fl/interest/otfl_dvsredstv/?utm_source=openai))

## 1.4. Реальный путь по Steam

**Самый реалистичный вариант:** онбординг как individual / sole proprietor, W‑8BEN, российский ИНН как foreign TIN, реальный иностранный банковский счёт на своё имя, paid game / DLC / Steam microtransactions. Стоимость: **$100 за app**, плюс возможные банковские комиссии. Срок: минимум 21 дней после оплаты app fee + минимум 2 недели publicly visible “coming soon” page; review store/build обычно 1–5 дней. ([partner.steamgames.com](https://partner.steamgames.com/doc/gettingstarted/onboarding?language=english))

**Не рекомендую:** пытаться монетизировать Steam-версию рекламой. Steam прямо указывает advertising-based business models среди нежелательного/запрещаемого контента. ([partner.steamgames.com](https://partner.steamgames.com/doc/gettingstarted/onboarding?language=english))

---

# 2. Google Play

## 2.1. Можно ли зарегистрировать аккаунт из РФ

**Проверено по официальным правилам Google Play.** В таблице supported locations у Google Play Россия отмечена как страна, где поддержаны и **developer registration**, и **merchant registration**, валюта — USD. ([support.google.com](https://support.google.com/googleplay/android-developer/answer/9306917))

Для personal account Google требует developer name, legal name, legal address, contact email/phone и developer email; legal name/address берутся из Google Payments profile и должны быть верифицированы до публикации. Если разработчик монетизирует приложения, Google показывает полный адрес. ([support.google.com](https://support.google.com/googleplay/android-developer/answer/13628312?hl=en))

Для organization account нужны D‑U‑N‑S, organization name/address, website, phone, contact data и т. д.; Google прямо пишет, что без D‑U‑N‑S создать organization account нельзя, кроме отдельных исключений. ([support.google.com](https://support.google.com/googleplay/android-developer/answer/13628312?hl=en))

Для personal account нужна official government identity document, верификация email/phone, а для новых personal accounts также device verification. Google пишет, что аккаунт должен быть верифицирован до подачи приложений на рассмотрение. ([support.google.com](https://support.google.com/googleplay/android-developer/answer/10841920?hl=en-419))

Дополнительно: personal developer accounts, созданные после 13 ноября 2023 г., должны пройти closed testing — минимум **12 testers**, opt‑in непрерывно не менее **14 дней**, прежде чем приложение можно будет сделать доступным в Google Play. ([support.google.com](https://support.google.com/googleplay/android-developer/answer/14151465?hl=en-en&utm_source=openai))

## 2.2. Что блокирует монетизацию Google Play из РФ

Главный блокер — не сам аккаунт разработчика, а **платежи и seller services**.

1. Для пользователей в России Google Play Billing приостановлен с 10 марта 2022 г.: пользователи в РФ не могут покупать приложения, делать IAP или подписки через Google Play; free apps доступны. Google также блокирует загрузку paid apps и updates к paid apps в России/Беларуси. ([support.google.com](https://support.google.com/googleplay/android-developer/answer/11950272?hl=en))

2. С 26 декабря 2024 г. Google Play **indefinitely suspends seller services** для Play developers, которые используют **disbursement bank account located in Russia**. Такие разработчики больше не могут монетизировать через Google Play: paid apps, IAP, subscriptions и renewals fail. Финальная выплата была предусмотрена на 15 января 2025 г. ([support.google.com](https://support.google.com/googleplay/android-developer/answer/15685001?hl=en&ref_topic=15819563))

3. Google Play требует, чтобы bank account для merchant payouts был **в той же стране/регионе, где зарегистрирован merchant account**. Для России в банковских реквизитах указаны wire transfer from the United States, USD, SWIFT/BIC/IBAN/intermediary fields. ([support.google.com](https://support.google.com/paymentscenter/answer/7161440))

Отсюда практический тупик: Россия как merchant location формально есть, но российский disbursement bank account делает monetization невозможной; иностранный банк для российского merchant profile в официальном общем правиле не проходит из-за “same country or region”. Google в санкционном FAQ советует альтернативный bank/eWallet, но технически это зависит от того, что Play Console реально даёт добавить для конкретного payments profile. ([support.google.com](https://support.google.com/googleplay/android-developer/answer/11958934?hl=en&ref_topic=15819563))

## 2.3. Примет ли Google Play сингапурский счёт/карту

**Карта — нет**, для payouts нужна не карта, а disbursement bank/payment account.

Сингапурский payment account официально описан для **developers based in Singapore**: Google Payment Singapore Pte. Ltd. может платить на nominated payment account, и разработчику рекомендуют заранее убедиться, что PSP примет такие выплаты. Но это относится к Singapore-based developers, а не к российскому payments profile. ([support.google.com](https://support.google.com/googleplay/android-developer/answer/7161440?hl=en&ref_topic=7279290))

Вывод: сингапурский счёт из “Платипо” может помочь только если он является полноценным payment/bank account на имя разработчика и если у разработчика есть законное основание создать Singapore payments profile. Просто российскому физлицу с российским legal address подставить сингапурскую карту вместо российского disbursement bank account — **нерабочий/высокорисковый вариант**.

## 2.4. Реальный путь по Google Play

**Вариант А — free app без Google Play monetization.** Российский personal account, identity verification, closed testing 12/14, публикация free app. Доход — не от Google Play, а от рекламы/внешней монетизации там, где это разрешено правилами. Для российских пользователей это самый реалистичный путь.

**Вариант Б — иностранная структура.** Открыть юрлицо/ИП в стране, где Google поддерживает merchant registration, создать payments profile этой страны, банковский счёт той же страны, D‑U‑N‑S для organization account. Google поддерживает merchant registration, например, в Armenia, Kazakhstan, Serbia, UAE, Singapore; но **Georgia в таблице Google Play имеет developer registration ✔, merchant registration ✘**, то есть для Google Play Billing Грузия как самостоятельная точка монетизации не подходит. ([support.google.com](https://support.google.com/googleplay/android-developer/answer/9306917))

**Вариант В — publisher.** Иностранный издатель публикует игру в своём Google Play account, получает выручку и платит разработчику по договору. Это рабоче, но разработчик отдаёт часть revenue и контроль.

---

# 3. App Store

## 3.1. Можно ли зарегистрироваться из РФ

**Проверено по официальным правилам Apple.** Apple Developer Program допускает enrollment as individual or organization; для individual нужны Apple Account с 2FA, legal name, email, phone, address, без PO box. Для organization нужны legal entity, authority to bind, D‑U‑N‑S, work email, website. Стоимость — **$99/year**. ([developer.apple.com](https://developer.apple.com/programs/enroll/))

Apple проводит compliance review: проверяет, что разработчик/организация не находится в embargoed countries и не фигурирует в restricted party lists. Для individual/user review может потребоваться government issued ID; для bank account review — ID, совпадающий с именем на bank account, или business registration для компании. ([developer.apple.com](https://developer.apple.com/help/app-store-connect/reference/account-management/compliance-review))

Наличие отдельного **Russian Developers Addendum** подтверждает, что Apple предусматривает membership located in Russia; addendum действует для участников Apple Developer Program, чьё membership located in Russia. ([developer.apple.com](https://developer.apple.com/contact/request/download/russian_developer_addendum.pdf))

Что реально блокирует: санкционный/embargo status, невозможность оплатить $99 российской картой, автоматические fraud/risk flags, несовпадение имени Apple Account/ID/bank, отсутствие D‑U‑N‑S для организации, проблемы с compliance review.

## 3.2. Монетизация в России через App Store

С 1 апреля 2026 г. Apple сообщает, что новые покупки в App Store и других Apple Media Services, включая IAP и subscription renewals, **больше недоступны в России**, если у пользователя нет средств на Apple Account balance. Также с 1 апреля 2026 нельзя использовать payment processing для пополнения Apple Account balance в России. ([support.apple.com](https://support.apple.com/en-gb/126891))

Значит, App Store monetization для российской аудитории через paid apps/IAP/subscriptions практически не работает. Для нероссийской аудитории App Store Billing продолжает работать, если у разработчика есть Paid Apps Agreement, tax forms и bank account.

Apple также допускает внешние purchase links в отдельных регионах/по entitlement, включая EEA и Russia, но это не “свободный обход”: нужен entitlement/условия Apple, корректная реализация StoreKit external purchase link и соблюдение App Review Guidelines. ([developer.apple.com](https://developer.apple.com/documentation/storekit/external-purchase?utm_source=openai))

## 3.3. Выплаты Apple и сингапурский счёт/карта

Чтобы получать выплаты, Apple требует: Paid Apps Agreement, banking information в App Store Connect, достижение monthly threshold и налоговые формы. Выплаты идут на primary bank account, multiple/split bank accounts не поддерживаются; срок — within 45 days after fiscal month end; способ — direct deposit/EFT. ([developer.apple.com](https://developer.apple.com/help/app-store-connect/getting-paid/overview-of-receiving-payments))

В banking information Apple просит выбрать bank country/region, currency, account number/IBAN, holder details; account number должен принадлежать legal entity or individual enrolled in Apple Developer Program, а данные должны совпадать с банковскими, иначе payment may be rejected. ([developer.apple.com](https://developer.apple.com/help/app-store-connect/manage-banking-information/enter-banking-information/))

По налогам для non‑US-based developers Apple требует W‑8BEN/W‑8BEN‑E/W‑8ECI в зависимости от ответов tax flow, плюс иногда дополнительные формы по стране. ([bb.jaff.eu.org](https://bb.jaff.eu.org/https/developer.apple.com/help/app-store-connect/manage-tax-information/provide-tax-information/))

**Карта Сингапура не является payout instrument.** Если “Платипо” даёт только карту — Apple на неё не платит. Если это реальный счёт/платёжный счёт на имя разработчика с реквизитами, Apple теоретически может принять его как bank country Singapore, но это зависит от App Store Connect validation и bank account review. Если счёт не на имя разработчика или это pooled/intermediary account, риск отказа высокий.

## 3.4. Реальный путь по App Store

**Самый реалистичный вариант без иностранного юрлица:** enroll as individual, оплатить $99 иностранной картой, пройти ID/compliance, подключить Paid Apps Agreement, W‑8BEN и реальный банковский счёт на имя разработчика. Монетизировать IAP/paid app в нероссийских storefronts; российскую аудиторию — free/ad-supported или через легально оформленные external purchase links, если Apple выдаст entitlement.

**Если цель — нормальные global IAP/подписки + меньше KYC-риска:** зарубежная компания/ИП + D‑U‑N‑S + корпоративный счёт.

---

# 4. Рекламные сети

## 4.1. AdMob / AdSense / Google Ad Manager

**Проверено официально:** Google с марта 2022 приостановил создание новых российских аккаунтов AdSense, AdMob и Google Ad Manager; с августа 2024 приостановил возможность Russia-based publishers монетизироваться через AdSense/AdMob/Ad Manager. ([support.google.com](https://support.google.com/publisherpolicies/answer/15766875?hl=en&utm_source=openai))

AdSense отдельно сообщил о deactivation всех Russia-based AdSense accounts с выплатой остатков при выполнении условий. ([support.google.com](https://support.google.com/adsense/answer/15282937?hl=en&utm_source=openai))

Для AdMob в январе 2025 Google уточнил: AdMob campaigns и AdMob Network по-прежнему не serve to users located in Russia, но AdMob publishers могут управлять third-party waterfall mediation ad sources для России. Это помогает только тем, у кого AdMob account не заблокирован как Russia-based и кто использует mediation. ([support.google.com](https://support.google.com/publisherpolicies/answer/15766875?hl=en&utm_source=openai))

**Вывод:** для российского самозанятого без иностранного аккаунта AdMob — практически закрыт. Использовать AdMob как основной источник дохода нельзя.

## 4.2. Яндекс Рекламная сеть / Yandex Mobile Ads / Yandex Mediation

Для резидента РФ это самый практичный рекламный путь. Яндекс прямо поддерживает работу физических лиц-резидентов РФ как **самозанятых** в РСЯ. ([yandex.ru](https://www.yandex.ru/support/partner/ru/payments/with-self-employed?utm_source=openai))

Яндекс указывает, что самозанятые могут получать выплаты на банковский счёт или через СБП; лимит НПД — 2,4 млн руб. в год, ставка при сотрудничестве с ООО “Яндекс” — 6%. ([yandex.ru](https://yandex.ru/project/yan/npd?utm_source=openai))

Для мобильных приложений у Яндекса есть **Yandex Mediation** — бесплатная платформа, позволяющая показывать рекламу из нескольких рекламных сетей; среди подключаемых источников указан VK Реклама. ([ads.yandex.com](https://ads.yandex.com/helpcenter/ru/monetization/yandex-mediation/?lang=ru&utm_source=openai))

По выплатам для mobile ads в FAQ Яндекса указан порог **3000 руб.** и документооборот через интерфейс РСЯ. ([ads.yandex.com](https://ads.yandex.com/helpcenter/ru/support/faq/payment?utm_source=openai))

**Вывод:** для Android/RuStore/Google Play free app и, возможно, iOS free app это основной “белый” способ получать рекламный доход в РФ как самозанятый.

## 4.3. AppLovin

Официально AppLovin указывает payment methods: direct deposit/ACH, wire transfer, check, PayPal; minimum threshold $100; часть методов может быть недоступна из-за local regulations. Платёжная информация может валидироваться AppLovin payments team. ([support.applovin.com](https://support.applovin.com/en/max/faq/faq-applovin-monetization-payment?utm_source=openai))

Я не нашёл в доступных официальных правилах AppLovin явного актуального запрета “Russia-based publishers cannot register/monetize” на уровне, аналогичном Google AdMob. Но это не означает, что российский аккаунт точно примут: AppLovin — американская компания, KYC/sanctions/payment processors могут отфильтровать российские адреса, банки или документы.

**Практический вывод:** можно тестировать только если в dashboard доступен способ выплаты на реальный счёт/PayPal/прочее на имя разработчика. Сингапурская карта сама по себе не решает payout.

## 4.4. Unity Ads / Unity LevelPlay

Официальная документация Unity по платежам говорит, что publishers получают automated payouts monthly и должны настроить payout profile для Unity Ads earnings. ([docs.unity.com](https://docs.unity.com/en-us/monetization/payments/intro-to-monetization-payments?utm_source=openai))

Я не нашёл свежей официальной страницы Unity с однозначным правилом “Russia-based publishers accepted/rejected in 2026”. Из отзывов разработчиков 2022 г. видно, что санкции США/экспортные ограничения влияли на отношения Unity с publishers/suppliers in Russia, Belarus and certain regions of Ukraine, но это старые developer reports, не текущая официальная политика 2026. ([reddit.com](https://www.reddit.com/r/Unity3D/comments/uf7113?utm_source=openai))

**Практический вывод:** Unity/LevelPlay можно рассматривать как часть mediation, но перед интеграцией нужно открыть аккаунт, пройти payout/KYC и получить письменный ответ поддержки по Russia residency и bank country. Не строил бы бизнес-план только на Unity Ads для российского физлица.

## 4.5. VK Ads / myTarget / Mintegral / ironSource и прочие

Я не успел найти достаточно официальных актуальных документов по каждой сети. Практически для RU-аудитории обычно смотрят Yandex + VK, а для global traffic — AppLovin MAX / Unity LevelPlay / Mintegral / ironSource, но для российского физлица ключевой вопрос всегда один: **примут ли KYC и куда смогут платить**.

---

# 5. Самозанятость, иностранная выручка, зарубежный счёт

## 5.1. Можно ли самозанятому получать от иностранной компании

**Собственный вывод из режима НПД:** да, если это доход от самостоятельной деятельности, не запрещённой для НПД, без сотрудников и в пределах лимита 2,4 млн руб./год. Место регистрации клиента само по себе не делает доход запрещённым. Для иностранных компаний ставка обычно 6%, как для юрлиц/организаций.

Но есть тонкость: договоры Steam/Apple/Google могут юридически оформлять доход как royalty, proceeds, commissionaire/agency proceeds. Для НПД это обычно не фатально, если разработчик продаёт собственный цифровой продукт/права, но лучше иметь договор/отчёты платформы и фиксировать чек на фактически полученную сумму.

## 5.2. Валютный контроль и зарубежный счёт

Если сингапурский продукт — это **счёт в иностранном банке или иной иностранной финансовой организации**, российский валютный резидент обычно должен уведомить ФНС об открытии/закрытии/изменении реквизитов. ФНС также описывает обязанность отчёта о движении средств по зарубежным счетам и исключение по порогу 600 000 руб. при выполнении условий. ([nalog.gov.ru](https://www.nalog.gov.ru/rn77/fl/interest/otfl_dvsredstv/?utm_source=openai))

Особо важно: если “Платипо” оформляет не персональный банковский счёт, а платёжный инструмент/кошелёк/субсчёт у посредника, надо выяснить юридический тип: bank account, payment account, e‑money wallet, FBO account. От этого зависит и отчётность в РФ, и то, примут ли его Steam/Apple/Google.

## 5.3. Налоги

Для НПД: при выплатах от юрлиц — 6%, лимит 2,4 млн руб./год. Если доход превысит лимит, НПД слетает для сверхлимитной части/дальнейших доходов, и нужен другой режим — ИП УСН, АУСН, иностранная компания и т. д. Яндекс в своих материалах для самозанятых прямо указывает, что при потере НПД можно продолжить как ИП по условиям для юрлиц/ИП. ([yandex.ru](https://yandex.ru/project/yan/npd?utm_source=openai))

---

# 6. Рабочие варианты на 2026 год

## Вариант 1. Самопубликация из РФ + иностранный счёт физлица

**Подходит:** Steam, частично App Store, free Google Play.  
**Не подходит:** полноценный Google Play Billing из РФ.

Что нужно: реальный счёт на имя разработчика, не санкционный банк/PSP, документы ID, российский ИНН, адрес, W‑8BEN, уведомления ФНС по зарубежному счёту.

Ориентировочно:  
- Steam: $100/app, 3–6 недель до релиза с учётом waiting period/coming soon/review.  
- Apple: $99/year, от нескольких дней до недель на enrollment/compliance.  
- Google Play: $25 one-time fee, identity/device verification + 12 testers/14 days для нового personal account.  

Главный риск: “карта через посредника” не равна payout account.

## Вариант 2. Free-to-play без IAP + реклама через Яндекс/VK

**Подходит:** RuStore, Google Play free app, App Store free app.  
**Не подходит:** Steam как advertising-based business model.

Это самый реалистичный mobile route для человека без зарубежного юрлица. Google Play/App Store дают дистрибуцию, но деньги приходят не от магазинов, а от рекламной сети. Для РФ-аудитории — Яндекс РСЯ как самозанятый. ([yandex.ru](https://www.yandex.ru/support/partner/ru/payments/with-self-employed?utm_source=openai))

## Вариант 3. Иностранный издатель

**Подходит:** Steam, Google Play, App Store.  
Издатель публикует игру на своих аккаунтах, собирает выручку, платит разработчику revenue share/royalties.

Ориентировочно:  
- Инди-издатель Steam: 20–50% revenue share, иногда recoup marketing/localization/QA.  
- Mobile publisher: часто 30–70% в зависимости от UA, creatives, ASO, LiveOps.  
- Срок: 1–3 месяца на переговоры, due diligence, сборки, договоры.

Плюсы: не нужен свой payout у Apple/Google/Steam.  
Минусы: контроль, IP, отчётность, риск недобросовестного издателя.

## Вариант 4. Зарубежное ИП/юрлицо

Ориентиры по странам:

| Страна | Для Steam | Для Apple | Для Google Play | Примерная стоимость/срок | Комментарий |
|---|---:|---:|---:|---|---|
| **Казахстан** | Да | Да | Да | ~$500–2000, 2–8 недель | Google merchant supported; банки KYC к россиянам строгие. |
| **Армения** | Да | Да | Да | ~$300–1500, 1–6 недель | Google merchant supported; часто рассматривается как доступный вариант. |
| **Сербия** | Да | Да | Да | ~$800–3000+, 1–2 месяца | Дороже бухгалтерия/банк, но более “европейская” инфраструктура. |
| **ОАЭ** | Да | Да | Да | ~$3000–8000+/год, 1–3 месяца | Дорого, но сильная платёжная инфраструктура; substance/KYC. |
| **Грузия** | Да | Да | **Нет для Google merchant** | ~$200–1000+, быстро | Google Play developer registration есть, merchant registration нет. ([support.google.com](https://support.google.com/googleplay/android-developer/answer/9306917)) |
| **Сингапур** | Да | Да | Да | дорого, обычно $2000–6000+ setup/год | Хорошо для платежей, но нужна реальная структура/адрес/банк. |

Для Apple organization account почти всегда нужен D‑U‑N‑S; Apple говорит, что D‑U‑N‑S используется для проверки identity/legal entity/address. ([developer.apple.com](https://developer.apple.com/programs/enroll/)) Google organization account тоже требует D‑U‑N‑S. ([support.google.com](https://support.google.com/googleplay/android-developer/answer/13628312?hl=en))

## Вариант 5. “Номинальные аккаунты”, чужие карты, фиктивный адрес

Не рекомендую. У Apple/Google/Steam везде KYC, sanctions screening, bank name match, tax forms. Несовпадения могут привести к hold выплат, отказу, бану аккаунта и потере игры.

---

# 7. Итог по каждой площадке

## Steam — **да, пробовать напрямую**

Лучший путь: individual/sole proprietor, paid game, W‑8BEN, реальный иностранный счёт на имя разработчика. Не использовать рекламную модель. Если сингапурский продукт “Платипо” — только карта, не годится; если это полноценный счёт на имя разработчика с SWIFT/реквизитами, можно пробовать, но KYC не гарантирован.

## Google Play — **free app напрямую, платная монетизация через иностранную структуру/издателя**

Российский personal developer account формально возможен, но Google Play Billing для российской аудитории не работает, а monetization для разработчиков с российским payout bank account приостановлена. Самый реалистичный путь — free app + Яндекс/VK Ads; для IAP/paid apps globally — Казахстан/Армения/Сербия/ОАЭ/Сингапур или издатель.

## App Store — **можно напрямую, но деньги в основном не из России**

Enroll as individual, оплатить membership иностранной картой, пройти ID/compliance, указать реальный bank account на своё имя, W‑8BEN. Российская аудитория почти не платит через Apple после 1 апреля 2026, поэтому монетизация — global IAP/paid app или реклама. Для внешних платежей в Russia storefront — только аккуратно через Apple entitlement/правила.

## Реклама — **Яндекс как основной вариант для РФ**

AdMob для Russia-based publisher закрыт. Яндекс РСЯ официально поддерживает самозанятых РФ, выплаты на счёт/СБП, ставка НПД 6%, mobile mediation есть. AppLovin/Unity — можно тестировать для global traffic, но не считать гарантированным payout-каналом для российского физлица без проверки KYC.