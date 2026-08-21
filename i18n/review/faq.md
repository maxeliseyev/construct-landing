# faq

Edit the Russian only — the `##` heading is the key the site looks the
string up by, and the `>` line is the English original for reference.
When you are done: `python3 scripts/ru-review.py import`

## faq.contacts.contacts  ·  plain text

> Contacts

Контакты

## faq.contacts.p3  ·  plain text

> The system is designed so that a stranger cannot simply start messaging you. To start a conversation, one of you shares a QR code or an invite link and the other scans or follows it. Those are single-use and expire in twelve hours — a link that has been accepted once cannot be accepted again. Separately, you may switch on discovery in settings and be findable by username; that is off by default, so unless you turn it on, an invite is the only way in.

Система устроена так, что незнакомый человек не может просто начать вам писать. Чтобы начать разговор, один делится QR-кодом или инвайт-ссылкой, а другой сканирует её или переходит по ней. Они одноразовые и живут двенадцать часов — принятую однажды ссылку использовать повторно нельзя. Отдельно вы можете включить в настройках обнаружение и стать находимым по имени пользователя; по умолчанию оно выключено, так что пока вы его не включили, инвайт — единственный путь.

## faq.contacts.p5  ·  plain text

> It's an intentional design choice. In most messengers, knowing someone's phone number or username is enough to start flooding them with messages. Here, mutual consent is baked into the architecture — not just declared in a privacy policy.

Это намеренное решение. В большинстве мессенджеров достаточно знать номер телефона или никнейм, чтобы начать засыпать человека сообщениями. Здесь взаимное согласие зашито в архитектуру, а не просто задекларировано в политике.

## faq.contacts.p7  ·  plain text

> A code can be accepted only once, so a shared link lets in at most one person, and a link that has already been used does nothing at all. It also stops working twelve hours after it was created. If someone does get in, you will see a new conversation and can block them immediately.

Код принимается только один раз, поэтому по разошедшейся ссылке сможет добавиться не больше одного человека, а уже использованная ссылка не сделает ничего. Кроме того, код перестаёт действовать через двенадцать часов после создания. Если кто-то всё же добавился, вы увидите новый разговор и сможете сразу его заблокировать.

## faq.contacts.q2  ·  plain text

> How do I message someone?

Как написать кому-то?

## faq.contacts.q4  ·  plain text

> Why this restriction? Isn't it inconvenient?

Зачем такое ограничение? Это же неудобно.

## faq.contacts.q6  ·  plain text

> What if someone shares my QR code without my permission?

Что будет, если кто-то поделится моим QR-кодом без моего ведома?

## faq.demo-title.back-to-home  ·  plain text

> Back to home

На главную

## faq.demo-title.open-cryptography-demo  ·  plain text

> Open Cryptography Demo

Открыть демо криптографии

## faq.demo-title.privacy-policy  ·  plain text

> Privacy Policy

Политика конфиденциальности

## faq.demo-title.t2  ·  plain text

> An interactive cryptography demo shows how key exchange, Double Ratchet, and post-quantum algorithms work step by step. Available for testers and the curious.

Интерактивное демо криптографии показывает пошагово как работает обмен ключами, Double Ratchet и постквантовые алгоритмы. Доступно для тестировщиков и любопытных.

## faq.demo-title.want-to-see-it-in-action  ·  plain text

> Want to see it in action?

Хотите посмотреть, как это работает?

## faq.encryption.encryption-amp-privacy  ·  plain text

> Encryption & Privacy

Шифрование и приватность

## faq.encryption.p10  ·  HTML allowed

> Honest limits: Stealth hides the sender <em>identity</em> from the server, not message timing, size, or your IP address — those remain visible at the network/transport layer. Privacy Pass tokens can ride along for anti-spam; server-side enforcement is still rolling out, so treat token-based rate control as maturing, not finished.

Ограничения: Защита отправителя скрывает его <em>личность</em> от сервера, но не время, размер или IP — это видно на сетевом/транспортном уровне. Токены Privacy Pass могут идти вместе с sealed-отправкой для анти-спама; server-side enforcement ещё раскатывается — rate-control на токенах считается зреющим, не завершённым.

## faq.encryption.p12  ·  HTML allowed

> No — none. No analytics, no usage metrics, no behavioural events, no crash phone-home, no advertising identifiers. Not "collected and anonymised" — <em>not collected</em>. The app has no third-party trackers (no Firebase, Crashlytics, Sentry, Amplitude, Segment); its only external dependencies are transport/media infrastructure and an on-device ML library. Production builds also write <strong>no diagnostic logs to disk</strong> and expose no debug or log-export screen. When we need logs to fix a bug, it is you who taps "share" in a beta build — never a silent upload.

Нет — вообще. Никакой аналитики, метрик использования, поведенческих событий, отправки крашей, рекламных идентификаторов. Не «собрано и обезличено» — <em>не собрано вовсе</em>. В приложении нет сторонних трекеров (ни Firebase, ни Crashlytics, ни Sentry, ни Amplitude, ни Segment); единственные внешние зависимости — транспорт/медиа и on-device ML-библиотека. Релизные сборки к тому же <strong>не пишут диагностических логов на диск</strong> и не дают экрана дебага или экспорта логов. Когда нам нужны логи для починки бага, их отправляете вы кнопкой «поделиться» в бета-сборке — никакой тихой отправки.

## faq.encryption.p3  ·  HTML allowed

> All messages are encrypted on the sender's device before transmission and can only be decrypted on the recipient's device. The server sees only an encrypted stream and routes it — it cannot read the content. Key establishment uses X3DH extended with post-quantum key agreement (<strong>PQXDH</strong>): the sender encapsulates an <strong>ML-KEM-768</strong> secret to the recipient's Kyber prekey and it is mixed into the ratchet, which is what limits "record now, decrypt with a quantum computer later". One honest detail: the contribution is applied after the first message, so message zero of a new conversation is protected classically and everything from the second message on is not. Messages then use Double Ratchet, which rotates keys with every message, so compromising one key exposes neither past nor future messages.

Все сообщения шифруются на устройстве отправителя перед отправкой и расшифровываются только на устройстве получателя. Сервер видит лишь зашифрованный поток и маршрутизирует его — прочитать содержимое он не может. Для установки сессии используется X3DH, расширенный постквантовым согласованием ключей (<strong>PQXDH</strong>): отправитель инкапсулирует секрет <strong>ML-KEM-768</strong> в Kyber-префикс получателя, и этот секрет подмешивается в ратчет — именно это ограничивает сценарий «записать сейчас, расшифровать квантовым компьютером потом». Важная деталь: вклад применяется после первого сообщения, поэтому нулевое сообщение нового разговора защищено классически, а всё начиная со второго — уже нет. Дальше работает Double Ratchet, меняющий ключи с каждым сообщением, так что компрометация одного ключа не раскрывает ни прошлых, ни будущих сообщений.

## faq.encryption.p5  ·  HTML allowed

> Very little, and none of it is you. To route a message the server needs an opaque account id for the recipient, the size of the ciphertext and the time it arrived; it also holds your public keys and a push token. That is the list. It does not see the content, your name, your avatar, your contact list — or, on the sealed-sender path that is always on, who sent the message. Delivered messages are not kept. A username is optional, is <strong>not</strong> used for routing, and is stored only as a keyed hash for the sole purpose of letting people find you — and that lookup is off until you switch discovery on, so by default an account cannot be found by name at all.

Очень мало, и ничто из этого — вы. Чтобы доставить сообщение, серверу нужны непрозрачный идентификатор аккаунта получателя, размер шифротекста и время получения; ещё он хранит ваши публичные ключи и push-токен. Это весь список. Он не видит ни содержимого, ни вашего имени, ни аватара, ни списка контактов — и, на постоянно включённом пути защиты отправителя, не видит, кто отправил сообщение. Доставленные сообщения не хранятся. Имя пользователя необязательно, в маршрутизации <strong>не</strong> участвует и хранится только ключевым хешем ради одной задачи — чтобы вас могли найти; сам поиск выключен, пока вы не включите обнаружение, так что по умолчанию аккаунт нельзя найти по имени вообще.

## faq.encryption.p7  ·  HTML allowed

> This is the harder part. The server can still observe that <em>someone</em> delivered ciphertext to device B (recipient, time, size). With always-on <strong>Stealth (sealed sender)</strong>, it does <em>not</em> learn who sent that ciphertext — see the next question. Censorship protection partially obscures the network path. Full anonymity at the routing layer (hiding from the recipient's side and from network-level IP/timing correlation too) is a problem of a different order of magnitude and isn't solved today.

Это более трудная часть. Сервер всё ещё видит, что <em>кто-то</em> доставил шифротекст устройству B (получатель, время, размер). При постоянно включённой <strong>защите отправителя</strong> он <em>не</em> узнаёт, кто именно написал, — см. следующий вопрос. Защита от блокировок частично скрывает сетевой путь. Полная анонимность на уровне маршрутизации (спрятаться и от получателя, и от корреляции по IP и таймингам) — задача другого порядка, и сегодня она не решена.

## faq.encryption.p9  ·  HTML allowed

> No — the sender field is left out of the envelope, and this is <strong>always on</strong> for ordinary traffic (messages, delivery receipts, call setup, profile sharing). There is no switch to forget. Your device seals a signed sender certificate to the recipient's key: the recipient can open it and verify who wrote, the server cannot. A few internal paths — keep-alives, syncing your own devices, session housekeeping — still carry a sender by design.<br /><br />It is worth being precise about what is being hidden, because it is not an identity. The server never had one: an account here is a keypair and an opaque id, with no phone number, email or real name attached, so there is nothing to link to a person in the first place. What sealed sender removes is the last link between two of those ids — who wrote to whom. The network layer is a separate matter and is covered above: timing and IP remain visible, and that is where a well-resourced observer works.

Нет — поле отправителя не кладётся в конверт, и это <strong>всегда включено</strong> для обычного трафика (сообщения, квитанции о доставке, установка звонка, обмен профилями). Переключателя, который можно забыть, нет. Ваше устройство запечатывает подписанный сертификат отправителя на ключ получателя: получатель может его открыть и проверить, кто написал, а сервер — нет. Несколько внутренних путей — поддержание соединения, синхронизация ваших собственных устройств, служебные сообщения сессии — по замыслу по-прежнему несут отправителя.<br /><br />Стоит уточнить, что именно скрывается, потому что это не личность. Её у сервера никогда и не было: аккаунт здесь — это пара ключей и непрозрачный идентификатор, без номера телефона, почты и настоящего имени, так что сопоставлять с человеком изначально нечего. Защита отправителя убирает последнюю связь между двумя такими идентификаторами — кто кому написал. Сетевой уровень — отдельный разговор, он выше: время и IP остаются видимыми, и именно там работает наблюдатель с ресурсами.

## faq.encryption.q11  ·  plain text

> Do you collect analytics or telemetry?

Вы собираете аналитику или телеметрию?

## faq.encryption.q2  ·  plain text

> How does encryption work?

Как работает шифрование?

## faq.encryption.q4  ·  plain text

> What exactly does the server see?

Что именно видит сервер?

## faq.encryption.q6  ·  plain text

> What about metadata? Who talks to whom?

А метаданные? Кто с кем общается?

## faq.encryption.q8  ·  plain text

> Does the server know who sent a message?

Знает ли сервер, кто отправил сообщение?

## faq.frequently-asked-questions  ·  plain text

> Frequently Asked Questions

Часто задаваемые вопросы

## faq.messages.messages  ·  plain text

> Messages

Сообщения

## faq.messages.p4  ·  plain text

> Yes, editing is supported. After changes, the message is marked as "edited". The edit propagates to the recipient's device through the same delivery mechanism as regular messages.

Да, редактирование поддерживается. После изменения у сообщения появляется пометка «изменено». Редактирование распространяется на устройство получателя через тот же механизм доставки, что и обычные сообщения.

## faq.messages.p6  ·  plain text

> Notifications are delivered through Apple Push Notification Service (APNs). A stable internet connection is required. If the phone is in airplane mode, behind a VPN with aggressive filtering, or Apple decided the push was "low priority" — the notification may be delayed or not arrive at all. When the app opens again, messages sync automatically.

Уведомления доставляются через Apple Push Notification Service (APNs). Нужно стабильное интернет-соединение. Если телефон в авиарежиме, за VPN с агрессивной фильтрацией или Apple сочла пуш «низкоприоритетным» — уведомление может прийти с задержкой или не прийти вообще. Когда приложение снова откроется, сообщения подтянутся автоматически.

## faq.messages.q2  ·  plain text

> What do delivery status indicators mean?

Что означают статусы у сообщений?

## faq.messages.q3  ·  plain text

> Can I edit sent messages?

Можно ли редактировать отправленные сообщения?

## faq.messages.q5  ·  plain text

> Why don't notifications arrive when the app is closed?

Почему иногда не приходят уведомления, когда приложение закрыто?

## faq.messages.status.delivered.name  ·  plain text

> Delivered

Доставлено

## faq.messages.status.delivered.what  ·  plain text

> the recipient's device decrypted it and sent back a confirmation

устройство получателя расшифровало его и прислало подтверждение

## faq.messages.status.failed.name  ·  plain text

> Failed

Не отправлено

## faq.messages.status.failed.what  ·  plain text

> it was rejected for a reason retrying will not fix, so nothing happens automatically; tap to try again

отклонено по причине, которую повтор не исправит, поэтому само ничего не произойдёт; нажмите, чтобы попробовать снова

## faq.messages.status.note  ·  plain text

> There is no "read" status, and that is deliberate: a read receipt would tell the sender when you opened the app, which is a fact about you that the message does not need. "Delivered" is an encrypted receipt from the recipient's device — not the server saying it forwarded something.

Статуса «прочитано» нет, и это сделано намеренно: отметка о прочтении сообщила бы отправителю, когда вы открыли приложение, — факт о вас, который сообщению не нужен. «Доставлено» — это зашифрованная квитанция от устройства получателя, а не сообщение сервера о том, что он что-то переслал.

## faq.messages.status.queued.name  ·  plain text

> Queued

В очереди

## faq.messages.status.queued.what  ·  plain text

> it has not gone out yet — the app keeps trying by itself; tap if you would rather not wait

ещё не ушло — приложение продолжает попытки само; нажмите, если не хотите ждать

## faq.messages.status.sending.name  ·  plain text

> Sending

Отправляется

## faq.messages.status.sending.what  ·  plain text

> being encrypted on your device

шифруется на вашем устройстве

## faq.messages.status.sent.name  ·  plain text

> Sent

Отправлено

## faq.messages.status.sent.what  ·  plain text

> it left your device and the server accepted it

ушло с устройства, сервер его принял

## faq.meta.title  ·  plain text

> FAQ — Konstruct Messenger

FAQ — Konstruct Мессенджер

## faq.profile.p3  ·  plain text

> Your Display Name and avatar live on your device; they are not part of your public profile and nobody can look them up. When you start a new conversation the other person sees only a generated pseudonym, deterministic — always the same for a given ID. To show them your real name and photo, open their profile and tap "Share Profile": both travel over the encrypted channel. One exception: if you send a contact request, your username and Display Name are attached to it so the recipient can tell who is asking. The server stores that snapshot encrypted at rest, under a key the server itself holds — it is not end-to-end encrypted, and your avatar is never included.

Ваше отображаемое имя и аватар живут на устройстве; они не часть публичного профиля, и найти их никто не может. Когда вы начинаете новый разговор, собеседник видит только сгенерированный псевдоним — детерминированный, для данного ID всегда один и тот же. Чтобы показать настоящее имя и фото, откройте профиль собеседника и нажмите «Поделиться профилем»: и то, и другое пойдёт по зашифрованному каналу. Одно исключение: при отправке запроса в контакты к нему прикладываются ваше имя пользователя и отображаемое имя, чтобы получатель понимал, кто просит. Сервер хранит этот снимок зашифрованным, но под собственным ключом — это не сквозное шифрование; аватар в снимок не входит никогда.

## faq.profile.p5  ·  plain text

> A blank name would be awkward — you'd see featureless rows in your chat list with no way to tell contacts apart. The generated name is stable: "Quick Falcon" is always "Quick Falcon" for that ID, on any device.

Пустое имя неудобно: в списке чатов вы видели бы безликие строки и не могли бы отличить один контакт от другого. Сгенерированное имя стабильно — «Быстрый Сокол» всегда будет «Быстрым Соколом» для этого ID, на любом устройстве.

## faq.profile.p7  ·  plain text

> Yes. Display priority: Display Name (if they shared it) → username → generated name. So if someone registered with @john, you'll see that, not "Peaceful Whale".

Да. Приоритет отображения: Display Name (если поделился) → username → сгенерированное имя. Если человек зарегистрировался с username @john, вы увидите именно его, а не «Мирный Кит».

## faq.profile.profile  ·  plain text

> Profile

Профиль

## faq.profile.q2  ·  plain text

> What is the Display Name for?

Зачем нужен Display Name?

## faq.profile.q4  ·  plain text

> Why a generated name instead of just blank?

Почему сгенерированное имя, а не просто пустое?

## faq.profile.q6  ·  plain text

> If someone has a username, do I see it?

Если у пользователя задан username, я его вижу?

## faq.registration.p3  ·  HTML allowed

> During registration, the app receives a cryptographic Proof of Work challenge from the server and solves it — this prevents automated bot registrations. At the same time, several cryptographic key sets are generated on-device: long-term identity keys, signed prekeys, and one-time prekeys (including post-quantum ML-KEM-768 keys). Only the public parts of these keys and the PoW result are sent to the server. Private keys never leave your device. Your identity <em>is</em> these keys — there's no password to steal or recover.

Во время регистрации приложение получает от
 сервера небольшую криптографическую задачу
 (Proof of Work) и решает её — это защита от
 автоматической регистрации ботами. Параллельно
 генерируются уникальные идентификаторы
 устройства и несколько наборов ключей
 шифрования: долгосрочные ключи идентичности,
 подписанные предварительные ключи и одноразовые
 предварительные ключи (включая постквантовые
 ML-KEM-768). На сервер уходят только публичные
 части этих ключей и результат PoW-задачи.
 Приватные ключи никогда не покидают устройство.
 Вместо пароля ваша идентичность — это и есть эти
 ключи.

## faq.registration.p5  ·  plain text

> Not yet. In conventional messengers, "sign out and back in" means entering a username and password. Here your identity is the cryptographic keys stored on your device — without them, you can't authenticate. Deleting the app is equivalent to losing your account.

Пока нет. В обычных мессенджерах "выйти и войти" означает ввести логин/пароль. Здесь ваша идентичность — это ключи на устройстве, и без них войти невозможно. Удаление приложения равнозначно потере аккаунта.

## faq.registration.p7  ·  plain text

> In Settings you can generate a seed phrase — a sequence of words that can reconstruct your private keys. It works the same way as a recovery phrase in crypto wallets. Write it down and keep it somewhere safe — this is the only way to transfer your account to a new device.

В настройках можно сгенерировать seed-фразу — последовательность слов, из которой можно восстановить приватные ключи. Это примерно то же самое, что фраза восстановления в криптокошельках. Запишите её и храните в надёжном месте — это единственный способ перенести аккаунт на новое устройство.

## faq.registration.q2  ·  plain text

> Why no username and password?

Почему не нужны логин и пароль?

## faq.registration.q4  ·  plain text

> Can I sign out and sign back in?

Можно ли выйти из аккаунта и войти заново?

## faq.registration.q6  ·  plain text

> How do I keep my account when switching phones?

Как не потерять аккаунт при смене телефона?

## faq.registration.registration-amp-account  ·  plain text

> Registration & Account

Регистрация и аккаунт

## faq.resilience.donate.list  ·  HTML allowed

> <li><strong>Monero (XMR)</strong> — recommended:<br /><code class="addr" title="Click to copy">496i5qvPzRtJPQjiPXnLvEGutjHFth4pWDQaJwbbMreyaTYg4qfbo48MXrTnYH32MHiAn5GcSEN1c48EYBvVkrx9Pi5BWvn</code></li><li><strong>Bitcoin (BTC)</strong>:<br /><code class="addr" title="Click to copy">bc1q5cthgu6k9utg9hk2mx2xshdtsrhvu54ysmqhmm</code></li><li><strong>Ko-fi</strong> — convenient but not private, the processor knows your identity:<br /><a href="https://ko-fi.com/construct_msg" rel="noopener noreferrer" target="_blank">ko-fi.com/construct_msg</a></li>

<li><strong>Monero (XMR)</strong> — рекомендуется:<br /><code class="addr" title="Нажмите, чтобы скопировать">496i5qvPzRtJPQjiPXnLvEGutjHFth4pWDQaJwbbMreyaTYg4qfbo48MXrTnYH32MHiAn5GcSEN1c48EYBvVkrx9Pi5BWvn</code></li><li><strong>Bitcoin (BTC)</strong>:<br /><code class="addr" title="Нажмите, чтобы скопировать">bc1q5cthgu6k9utg9hk2mx2xshdtsrhvu54ysmqhmm</code></li><li><strong>Ko-fi</strong> — удобно, но не приватно: платёжный сервис знает, кто вы:<br /><a href="https://ko-fi.com/construct_msg" rel="noopener noreferrer" target="_blank">ko-fi.com/construct_msg</a></li>

## faq.resilience.donate.p  ·  HTML allowed

> No ads, no data resale, no telemetry — the flip side is that Konstruct runs on voluntary donations. They go directly to development and the server. Prefer <strong>Monero (XMR)</strong> if you care about privacy — unlike Bitcoin its chain isn't public. Always cross-check an address against the project repository before sending, in case a page is tampered with.

Без рекламы, без перепродажи данных, без телеметрии — обратная сторона в том, что Konstruct живёт на добровольных донатах. Они идут напрямую на разработку и сервер. Если цените приватность — предпочтите <strong>Monero (XMR)</strong>, в отличие от биткоина его цепочка не публична. Перед отправкой всегда сверяй адрес с репозиторием проекта на случай подмены страницы.

## faq.resilience.network-resilience-amp-sustainability  ·  plain text

> Network Resilience & Sustainability

Устойчивость сети и жизнеспособность

## faq.resilience.p3  ·  HTML allowed

> Messaging stops until it returns. The alpha runs on a single trusted server, and there is no second path today — no relays, no peer-to-peer, no other instance to fall back to. Anything encrypted stays encrypted and nothing is lost; it simply will not move. Making that untrue is what the roadmap is about, and none of it has shipped.

Обмен сообщениями останавливается до его возвращения. Альфа работает на одном доверенном сервере, и второго пути сегодня нет — ни реле, ни соединений напрямую, ни другого узла, на который можно опереться. Всё зашифрованное остаётся зашифрованным, ничего не теряется — просто не движется. Дорожная карта существует ровно ради того, чтобы это перестало быть правдой, и ничего из неё пока не выпущено.

## faq.resilience.p5  ·  plain text

> Yes — unconditionally. Sending messages, receiving messages, E2EE, and all security features will never go behind a paywall. Donation-only models have historically proved fragile for privacy projects, so Konstruct plans a mix: voluntary donations, optional premium features (larger file transfers, extended history, custom themes — never security features), and B2B hosted instances for organizations. The core will always be free.

Да — безусловно. Отправка сообщений, получение сообщений, E2EE и все функции безопасности никогда не окажутся за платным барьером. Модель только на донатах исторически оказалась хрупкой для privacy-проектов, поэтому Конструкт планирует комбинацию: добровольные пожертвования, опциональные premium-функции (большие файлы, расширенная история, темы — никогда функции безопасности) и B2B-хостинг для организаций. Ядро всегда будет бесплатным.

## faq.resilience.p8  ·  HTML allowed

> <em>P2P mode is planned, not yet implemented — all traffic currently goes through the central server.</em> The target design: when both users are simultaneously online and connected to a Konstruct server, the server will signal them to upgrade to a direct peer-to-peer QUIC connection. Once established, the server exits the message relay path — traffic flows directly between devices. If either side goes offline, delivery falls back to the server.

<em>Режим P2P запланирован, но пока не реализован — весь трафик сейчас идёт через центральный сервер.</em> Целевой замысел: когда оба собеседника одновременно онлайн и подключены к серверу Konstruct, сервер даст им сигнал перейти на прямое P2P-соединение поверх QUIC. После установки сервер уходит с пути доставки — трафик идёт напрямую между устройствами. Если одна из сторон уходит в офлайн, доставка возвращается на сервер.

## faq.resilience.q2  ·  plain text

> What happens if Konstruct's servers go offline?

Что будет если серверы Конструкта отключатся?

## faq.resilience.q4  ·  plain text

> Will basic messaging always be free?

Базовый мессенджинг всегда будет бесплатным?

## faq.resilience.q6  ·  plain text

> How is Konstruct funded? Can I donate?

На что живёт Konstruct? Можно задонатить?

## faq.resilience.q7  ·  plain text

> What is P2P mode and when does it activate?

Что такое P2P-режим и когда он активируется?

## faq.security.p3  ·  plain text

> For this, the app has Lockdown Mode. When enabled, notifications only come from people who were in your contacts at activation time. Messages from new senders are still saved — they just won't disturb you. Useful if you're a public figure and want to temporarily close off from new contacts.

Для этого в приложении есть режим Lockdown. Когда он включён, уведомления и оповещения приходят только от людей, которые были у вас в контактах на момент его активации. Сообщения от новых отправителей всё равно сохраняются — они просто не будут вас тревожить. Режим полезен, если вы публичный человек и хотите временно закрыться от новых контактов.

## faq.security.p5  ·  plain text

> If a suspiciously high number of messages arrives from a single sender in a short time (more than ~10 in 30 seconds), the client automatically shows a warning and mutes notifications from them. You can then allow them (if it was a glitch) or block them. Importantly: this is receiver-side protection and works regardless of what client the attacker uses.

Если от одного отправителя приходит подозрительно много сообщений за короткое время (больше ~10 за 30 секунд), клиент автоматически покажет предупреждение и заглушит уведомления от него. Вы сможете либо разрешить его, либо заблокировать. Важно: это защита на стороне получателя и работает независимо от того, каким клиентом пользуется отправитель.

## faq.security.q2  ·  plain text

> What if strangers start mass-messaging me?

Что если мне начнут массово писать незнакомые люди?

## faq.security.q4  ·  plain text

> What if one person starts spamming hundreds of messages?

А если один конкретный человек начнёт спамить сотнями сообщений?

## faq.security.security-amp-protection  ·  plain text

> Security & Protection

Безопасность и защита

## faq.t2  ·  plain text

> How Konstruct works, why it works this way, and answers from users and testers.

Как работает Конструкт, почему именно так, и ответы на вопросы от пользователей и тестировщиков.

## faq.technical.p3  ·  plain text

> A session is an established encrypted channel between two devices. It's built on one-time keys that can't be reused, and keys rotate with every message. If the app was inactive for a long time, the device was reinstalled, or state desynchronization occurred — the session may stop decrypting incoming messages. In this case, automatic session healing kicks in: the app renegotiates keys and restores the channel in the background. Usually the user notices nothing — messages just start arriving again.

Сессия — это установленный зашифрованный канал между двумя устройствами. Она строится на одноразовых ключах, которые нельзя переиспользовать, и ключи вращаются с каждым сообщением. Если приложение долго не работало, устройство переустановили или произошла десинхронизация — сессия может перестать расшифровывать входящие сообщения. В этом случае запускается автоматическое «лечение» (session healing): приложение пересогласует ключи и восстанавливает канал в фоне. Пользователь, как правило, ничего не замечает.

## faq.technical.p5  ·  plain text

> Sync between multiple devices (phone + desktop) is in development. The desktop app exists as a prototype. Since identity is tied to keys rather than a server account, multi-device support requires a separate key-binding mechanism — we're working on it.

Синхронизация между несколькими устройствами (телефон + десктоп) находится в разработке. Десктоп-приложение существует как прототип. Поскольку идентичность привязана к ключам, а не к аккаунту на сервере, многоустройственность требует отдельного механизма привязки ключей — над этим работаем.

## faq.technical.p7  ·  HTML allowed

> Live messaging is a <strong>gRPC bidirectional MessageStream</strong> — one long-lived stream for heartbeats, inbound messages, and delivery receipts — not request/response polling. On current iOS builds the production path is <strong>QUIC</strong> (construct-transport); if QUIC is blocked or the handshake fails, the client falls back to <strong>gRPC over HTTP/2 + TLS&nbsp;1.3</strong> automatically. End-to-end encryption is independent of the transport: the wire only carries sealed ciphertext.

Live-сообщения идут по <strong>двунаправленному gRPC MessageStream</strong> — один долгоживущий поток для heartbeat’ов, входящих сообщений и receipt’ов, без request/response polling. На актуальных iOS-сборках боевой путь — <strong>QUIC</strong> (construct-transport); если QUIC режется или handshake не проходит, клиент автоматически падает на <strong>gRPC поверх HTTP/2 + TLS&nbsp;1.3</strong>. Сквозное шифрование не зависит от транспорта: по проводу едет только sealed ciphertext.

## faq.technical.q2  ·  plain text

> What is a "session" and why does it sometimes "break"?

Что такое «сессия» и почему она иногда «ломается»?

## faq.technical.q4  ·  plain text

> Is multiple-device support available?

Поддерживается ли несколько устройств?

## faq.technical.q6  ·  plain text

> What transport does Konstruct use for live messages?

Какой транспорт у Конструкта для live-сообщений?

## faq.technical.technical  ·  plain text

> Technical

Технические вопросы

## faq.testers.for-testers  ·  plain text

> For Testers

Для тестировщиков

## faq.testers.list3  ·  HTML allowed

> <li>Registration and adding a contact via QR code</li><li>Sending and receiving messages (both directions)</li><li>Delivery statuses — does a message reach "delivered", and do "queued" and "failed" retry when tapped?</li><li>Message editing — does the recipient see the changes?</li><li>Notifications with the app backgrounded</li><li>Behaviour with poor connectivity (airplane mode → restore)</li><li>Conversation recovery after app reinstall</li>

<li>Регистрация и добавление контакта по QR-коду</li><li>Отправка и получение сообщений (в обе стороны)</li><li>Статусы доставки — доходит ли сообщение до «доставлено», и повторяют ли отправку «в очереди» и «не отправлено» по нажатию?</li><li>Редактирование сообщений — видит ли получатель изменения?</li><li>Уведомления при свёрнутом приложении</li><li>Поведение на плохой связи (авиарежим → восстановление)</li><li>Восстановление переписки после переустановки приложения</li>

## faq.testers.p5  ·  HTML allowed

> In diagnostic (internal) builds the path is Settings → <strong>Diagnostics &amp; Logs</strong> → <strong>Share logs</strong>. Public builds keep <strong>no logs</strong> and do not compile that screen at all — if your build has no such row, describe the scenario and we will get a diagnostic build to you. The more precise the description (what you did, what you expected, what happened), the faster we can investigate. For a session issue, include logs from both devices.

В диагностических (внутренних) сборках путь такой: Настройки → <strong>Диагностика и логи</strong> → <strong>Поделиться логами</strong>. Публичные сборки логов <strong>не ведут</strong> и этот экран вообще не компилируют — если в вашей сборке такой строки нет, опишите сценарий, и мы выдадим вам диагностическую сборку. Чем точнее описание (что делали, что ожидали, что произошло), тем быстрее мы разберёмся. Для проблемы с сессией приложите логи с обоих устройств.

## faq.testers.p7  ·  HTML allowed

> In debug builds some components log on every UI update — that is normal for development. Lines like <code>FRC updated: 69 message(s) in window</code> are the chat list refreshing and do not indicate a problem.

В отладочных сборках некоторые компоненты пишут в лог при каждом обновлении интерфейса — для разработки это нормально. Строки вида <code>FRC updated: 69 message(s) in window</code> — это обновление списка чатов, они не означают проблемы.

## faq.testers.q2  ·  plain text

> What to check first?

Что проверять в первую очередь?

## faq.testers.q4  ·  plain text

> How to report a bug?

Как сообщить о баге?

## faq.testers.q6  ·  plain text

> Why are there so many repeated lines in the logs?

Почему в логах так много повторяющихся строк?

## faq.veil.censorship-protection  ·  plain text

> Censorship protection

Защита от блокировок

## faq.veil.p2  ·  HTML allowed

> There is a censorship-protection mode that changes how the app reaches the network when a direct connection is blocked or throttled. In Settings it is a single control with three positions — off, automatic, on — and automatic is the default: the app uses a direct connection while it works and switches only on demonstrated failure. There is nothing to configure and no addresses to enter; setup happens in the background. The implementation is open source (<code>construct-veil</code>, MPL-2.0), so the design can be reviewed by anyone.

В приложении есть режим защиты от блокировок: он меняет то, как приложение выходит в сеть, когда прямое соединение блокируется или душится. В настройках это один переключатель на три положения — выкл, автоматически, вкл, — и по умолчанию стоит «автоматически»: пока прямое соединение работает, используется оно, переключение происходит только после доказанного отказа. Настраивать нечего, адреса вводить не нужно, всё происходит в фоне. Реализация открыта (<code>construct-veil</code>, MPL-2.0), так что дизайн может изучить кто угодно.

## faq.veil.p4  ·  HTML allowed

> By default it is automatic — a direct connection is faster, so the app uses it while it works and switches only when it demonstrably fails. You can also force it on or off. What we deliberately do not publish is which techniques are live and where they currently do or do not get through: a public, up-to-date status report is free feedback for whoever is doing the blocking, and the app itself shows none of it either, for the same reason.

По умолчанию — автоматически: прямое соединение быстрее, поэтому пока оно работает, используется оно, а переключение происходит только при доказанном отказе. Можно также принудительно включить или выключить. Чего мы намеренно не публикуем — какие именно техники сейчас в строю и где они сейчас проходят или не проходят: публичная и актуальная сводка по этому вопросу есть бесплатная обратная связь для тех, кто блокирует. По той же причине этого не показывает и само приложение.

## faq.veil.q1  ·  plain text

> Does Konstruct work where messengers are blocked?

Работает ли Konstruct там, где мессенджеры блокируют?

## faq.veil.q3  ·  plain text

> Is censorship protection always on?

Защита от блокировок всегда включена?
