# home

Edit the Russian only — the `##` heading is the key the site looks the
string up by, and the `>` line is the English original for reference.
When you are done: `python3 scripts/ru-review.py import`

## home.about.our-mission  ·  plain text

> Our Mission

Наша миссия

## home.about.t10  ·  HTML allowed

> The server holds public keys and ciphertext, never plaintext, and does not see who sent a message — only the recipient, the time and the size. Timing and IP stay visible on the wire. Today the network is a single trusted server.

Сервер хранит публичные ключи и шифротекст, никогда открытый текст, и не видит, кто отправил сообщение, — только получателя, время и размер. Время и IP остаются видимыми на проводе. Сегодня сеть — это один доверенный сервер.

## home.about.t11  ·  HTML allowed

> <strong>What we will not build.</strong> No backdoor, whatever the pretext. No engagement mechanics — no infinite scroll, no streaks, no notification bait. No data resale: there is nothing to sell and no advertising business to feed.

<strong>Чего мы не будем делать.</strong> Никаких бэкдоров, под каким бы предлогом их ни просили. Никаких механик вовлечения — ни бесконечной ленты, ни серий, ни приманок в уведомлениях. Никакой перепродажи данных: продавать нечего, и рекламного бизнеса, который надо кормить, здесь нет.

## home.about.t3  ·  plain text

> Two positions we do not trade away:

Две позиции, которыми мы не торгуем:

## home.about.t4  ·  HTML allowed

> <strong>1. There is no safe backdoor.</strong> Any deliberate weakening of encryption creates a loophole, and whoever slips through it is not the one it was left for.

<strong>1. Безопасных бэкдоров не существует.</strong> Любое намеренное ослабление шифрования создаёт лазейку, и пройдёт по ней не тот, для кого её оставляли.

## home.about.t5  ·  HTML allowed

> <strong>2. Privacy by default.</strong> It has to hold without the user doing anything: a property of the protocol, not a setting.

<strong>2. Приватность по умолчанию.</strong> Она должна работать без действий пользователя: это свойство протокола, а не настройка.

## home.about.t9  ·  HTML allowed

> The implementation is the Signal Protocol design (X3DH + Double Ratchet), written from scratch in Rust and extended with post-quantum key agreement (ML-KEM-768).

Реализовано это на конструкции Signal Protocol (X3DH + Double Ratchet), написанной с нуля на Rust и дополненной постквантовым согласованием ключей (ML-KEM-768).

## home.alpha-build  ·  plain text

> ALPHA BUILD

ALPHA BUILD

## home.cta.install  ·  plain text

> Install the iOS beta

Поставить бету на iOS

## home.cta.server  ·  plain text

> What the server sees

Что видит сервер

## home.e2ee-active  ·  plain text

> E2EE::ACTIVE

E2EE::ACTIVE

## home.features.key-features  ·  plain text

> Key Features

Ключевые возможности

## home.features.t2  ·  HTML allowed

> <strong>End-to-end encryption by default</strong> — servers see only encrypted blobs.

<strong>Сквозное шифрование по умолчанию</strong> — серверы видят только зашифрованные данные.

## home.features.t3  ·  HTML allowed

> <strong>Forward secrecy</strong> — past messages stay secure even if keys leak.

<strong>Прямая секретность</strong> — прошлые сообщения остаются защищёнными даже при компрометации ключей.

## home.features.t4  ·  HTML allowed

> <strong>Post-quantum key agreement</strong> — <strong>ML-KEM-768</strong> (Kyber-768) is encapsulated to the recipient's Kyber prekey at session setup (PQXDH), and sessions that negotiate it also re-key continuously inside the Double Ratchet. Signatures are hybrid Ed25519 + <strong>ML-DSA-65</strong> (Dilithium-3): the crypto is implemented and cross-verified between client and server; client-side key rotation is still being wired up.

<strong>Постквантовое согласование ключей</strong> — <strong>ML-KEM-768</strong> (Kyber-768) инкапсулируется в Kyber-префикс получателя при установке сессии (PQXDH), а сессии, договорившиеся об этом, ещё и перевыдают ключи непрерывно внутри Double Ratchet. Подписи гибридные, Ed25519 + <strong>ML-DSA-65</strong> (Dilithium-3): криптография реализована и кросс-верифицирована между клиентом и сервером, оркестрация ротации ключей на клиенте ещё дописывается.

## home.features.t5  ·  HTML allowed

> <strong>Censorship protection</strong> — on by default. Direct while that works, switching only when it demonstrably stops.

<strong>Защита от блокировок</strong> — включена по умолчанию. Пока прямое соединение работает, используется оно; переключение только при доказанном отказе.

## home.features.t6  ·  HTML allowed

> <strong>Open source</strong> — clients, server and transport, under weak-copyleft licences. Running your own server is on the roadmap; the app cannot yet be pointed at one.

<strong>Открытый код</strong> — клиенты, сервер и транспорт под слабо-копилефтными лицензиями. Свой сервер — в планах: приложение пока нельзя на него направить.

## home.features.t7  ·  HTML allowed

> <strong>Zen UI</strong> — no notification spam, no social noise, focus on calm interaction.

<strong>Дзен-интерфейс</strong> — никакого спама уведомлений, никакого социального шума, только спокойное общение.

## home.features.t8  ·  HTML allowed

> <strong>Modern live transport</strong> — gRPC bidirectional MessageStream over <strong>QUIC</strong> (HTTP/2 fallback), censorship-resistant routing when the direct path is blocked, direct P2P planned when both peers are online.

<strong>Современный live-транспорт</strong> — двунаправленный gRPC MessageStream поверх <strong>QUIC</strong> (фолбэк на HTTP/2), обход блокировок когда прямой путь закрыт, прямой P2P — в планах, когда оба собеседника онлайн.

## home.get-involved.github  ·  plain text

> GitHub

GitHub

## home.get-involved.ios-testflight-public-alpha  ·  plain text

> iOS TestFlight Public Alpha

iOS TestFlight Public Alpha

## home.get-involved.open-source-amp-contributions  ·  plain text

> Open Source & Contributions

Открытый исходный код и участие

## home.get-involved.t2  ·  HTML allowed

> Konstruct is open source under weak-copyleft licenses: MPL-2.0 for the client apps and <code>construct-veil</code>, AGPL-3.0 for the server and relay, Apache-2.0 for shared libraries, and CC-BY-4.0 for text / specs. Privacy technology should be transparent and auditable by anyone — including the open issues we haven't fixed yet.

Konstruct открыт под слабо-копилефтными лицензиями: MPL-2.0 для клиентских приложений и <code>construct-veil</code>, AGPL-3.0 для сервера и реле, Apache-2.0 для общих библиотек, CC-BY-4.0 для текстов и спецификаций. Технология приватности должна быть прозрачной и проверяемой кем угодно — включая ещё не исправленные проблемы.

## home.get-involved.t3  ·  HTML allowed

> <strong>Contributions welcome</strong> — from code improvements to security review to documentation. We are a tiny team; PRs and issues are read by humans, not triaged by a queue.

<strong>Контрибьюторы приветствуются</strong> — от улучшений кода до review безопасности и документации. Команда крошечная: PR и issues читают живые люди, а не фильтрует очередь.

## home.get-involved.t5  ·  plain text

> Protocol specification & whitepaper

Спецификация протокола и whitepaper

## home.get-involved.t7  ·  plain text

> Report a security issue (GitHub private advisory)

Сообщить о security-проблеме (приватный advisory на GitHub)

## home.how-it-works.cryptography-stack  ·  plain text

> Cryptography Stack

Стек криптографии

## home.how-it-works.lead  ·  plain text

> The short version: messages are encrypted on your device, the server moves them without being able to read them, and it does not learn who sent them. The rest of this section is how, for readers who want it.

Короткая версия: сообщения шифруются на вашем устройстве, сервер переносит их, не умея прочитать, и не знает, кто отправил. Дальше — как именно, для тех, кому это интересно.

## home.how-it-works.t11  ·  HTML allowed

> <strong>gRPC bidirectional MessageStream over QUIC</strong> — the production path on iOS (construct-transport). One long-lived stream carries heartbeats, inbound messages and receipts without a TCP handshake per event, survives a change of network, and falls back to <strong>gRPC over HTTP/2 + TLS&nbsp;1.3</strong> automatically when QUIC is blocked. E2EE sits above it: the transport moves sealed ciphertext only, so changing it changes nothing about the guarantees.

<strong>Двунаправленный gRPC MessageStream поверх QUIC</strong> — боевой путь на iOS (construct-transport). Один долгоживущий поток несёт heartbeat’ы, входящие сообщения и квитанции без TCP-хендшейка на каждое событие, переживает смену сети и автоматически падает на <strong>gRPC поверх HTTP/2 + TLS&nbsp;1.3</strong>, когда QUIC режется. Сквозное шифрование лежит выше: транспорт переносит только запечатанный шифротекст, поэтому его смена ничего не меняет в гарантиях.

## home.how-it-works.t14  ·  HTML allowed

> <strong>Censorship resistance:</strong> when a direct TLS connection is blocked or throttled, the client routes through an obfuscation layer instead, automatically and with no user action. The implementation is open source (<code>construct-veil</code>, MPL-2.0) and the design is public. Operational detail — which transports are live, which entry points exist and where — is not published, and neither the app nor this site displays it.

<strong>Устойчивость к цензуре:</strong> когда прямое TLS-соединение блокируется или душится, клиент уходит через слой обфускации — автоматически и без действий пользователя. Реализация открыта (<code>construct-veil</code>, MPL-2.0), дизайн публичен. Операционные детали — какие транспорты сейчас в строю, какие точки входа существуют и где они — не публикуются, и ни приложение, ни этот сайт их не показывают.

## home.how-it-works.t2  ·  HTML allowed

> Konstruct uses <strong>gRPC with Protocol Buffers</strong> for efficient binary framing, and keeps a <strong>persistent bidirectional MessageStream</strong> open for real-time delivery — not request/response polling. The backend is split into independent services (identity, messaging, signaling, media) for fault isolation. Konstruct’s live path is <strong>gRPC bidi over QUIC</strong>, with HTTP/2 as automatic fallback.

Konstruct использует <strong>gRPC с Protocol Buffers</strong> для эффективного бинарного фрейминга и держит открытым <strong>постоянный двунаправленный MessageStream</strong> для доставки в реальном времени — без request/response polling. Бэкенд разделён на независимые сервисы (identity, messaging, signaling, media) для изоляции отказов. Боевой путь — <strong>gRPC bidi поверх QUIC</strong>, с автоматическим фолбэком на HTTP/2.

## home.how-it-works.t4  ·  HTML allowed

> <strong>X3DH + Double Ratchet (Signal Protocol design):</strong> end-to-end encryption with forward secrecy and post-compromise security (self-healing).

<strong>X3DH + Double Ratchet (дизайн Signal Protocol):</strong> сквозное шифрование с прямой секретностью и post-compromise security (самовосстановление).

## home.how-it-works.t5  ·  HTML allowed

> <strong>Post-quantum key agreement (PQXDH):</strong> when a session is established the initiator encapsulates an <strong>ML-KEM-768</strong> secret (NIST FIPS&nbsp;203) to the recipient's Kyber prekey and mixes it into the ratchet root, so a recorded session is not recoverable by breaking X25519 alone. The very first message is classical-only by design; the post-quantum secret applies from the second message onward. On top of that, sessions that negotiate it run a <strong>continuous ML-KEM-768 ratchet</strong> — re-keying as the conversation goes, not once at setup.

<strong>Постквантовое согласование ключей (PQXDH):</strong> при установке сессии инициатор инкапсулирует секрет <strong>ML-KEM-768</strong> (NIST FIPS&nbsp;203) в Kyber-префикс получателя и подмешивает его в корень ратчета — так что записанную сессию нельзя восстановить, сломав только X25519. Самое первое сообщение по замыслу остаётся классическим; постквантовый секрет действует со второго. Сверх этого сессии, которые об этом договорились, ведут <strong>непрерывный ратчет ML-KEM-768</strong> — перевыдача ключей по ходу разговора, а не один раз при установке.

## home.how-it-works.t6  ·  HTML allowed

> <strong>Authentication signatures: Ed25519</strong> today. Hybrid <strong>ML-DSA-65</strong> (Dilithium-3, NIST FIPS&nbsp;204) signing and verification are implemented and cross-verified between client and server; client-side key rotation orchestration is still in progress.

<strong>Подписи: Ed25519</strong> сегодня. Гибридные <strong>ML-DSA-65</strong> (Dilithium-3, NIST FIPS&nbsp;204) подпись и верификация реализованы и кросс-верифицированы между клиентом и сервером; оркестрация ротации ключей на клиенте ещё в работе.

## home.how-it-works.t7  ·  HTML allowed

> <strong>AEAD:</strong> ChaCha20-Poly1305 for message encryption. <strong>KDF:</strong> HKDF-SHA256 with domain-separation labels per protocol section. <strong>Anti-spam PoW:</strong> Argon2id.

<strong>AEAD:</strong> ChaCha20-Poly1305 для шифрования сообщений. <strong>KDF:</strong> HKDF-SHA256 с метками domain-separation для каждой секции протокола. <strong>Anti-spam PoW:</strong> Argon2id.

## home.how-it-works.t8  ·  HTML allowed

> <strong>Server is blind to content:</strong> messages are stored only as ciphertext; the server cannot decrypt. By default the server still sees delivery timestamps and recipient for routing. Eligible user traffic uses <strong>always-on sealed sender (Stealth)</strong> so the envelope omits the sender id — only the recipient can unseal who wrote. Privacy Pass anti-spam tokens can accompany sealed sends; server-side token enforcement is still rolling out.

<strong>Сервер не видит содержимого:</strong> сообщения хранятся только в виде шифротекста; сервер не может расшифровать. Для маршрутизации сервер видит время доставки и получателя. Подходящий пользовательский трафик идёт с <strong>постоянной защитой отправителя</strong> (в приложении — «стелс») — в конверте нет id отправителя, только получатель может раскрыть, кто написал. Токены Privacy Pass могут сопровождать sealed-отправки; server-side enforcement токенов ещё раскатывается.

## home.how-it-works.t9  ·  HTML allowed

> <strong>Crypto Agility:</strong> the protocol carries a suite version, so devices running different algorithm sets keep talking while a migration rolls out — no flag day, no requirement that everyone update at once. Adding an algorithm still means shipping a new build; what versioning removes is the need for it to happen everywhere simultaneously.

<strong>Криптоагильность:</strong> протокол несёт версию набора алгоритмов, поэтому устройства с разными наборами продолжают общаться, пока миграция раскатывается, — без flag day и без требования обновиться всем сразу. Добавление алгоритма по-прежнему означает новую сборку; версионирование убирает не её, а необходимость сделать это одновременно везде.

## home.how-it-works.technical-architecture  ·  plain text

> Technical Architecture

Техническая архитектура

## home.how-it-works.transport-layer  ·  plain text

> Transport Layer

Транспортный уровень

## home.identity.authorship  ·  HTML allowed

> Always-on sealed sender removes the sender's identifier from the message's metadata. The recipient can reveal who wrote it; the server cannot.

Постоянно включённая защита отправителя убирает его идентификатор из метаданных сообщения. Получатель может раскрыть, кто написал, а сервер — нет.

## home.identity.discovery  ·  HTML allowed

> With no address book there are no cold messages: a conversation starts from a QR code or an invite link — single-use and alive for twelve hours. Search by username exists, is optional, and is off until you turn it on.

Без телефонной книги нет «холодных» сообщений: разговор начинается с QR-кода или инвайт-ссылки — одноразовой и живущей двенадцать часов. Поиск по имени пользователя существует, он необязателен и выключен, пока вы его не включите.

## home.identity.lead  ·  HTML allowed

> Every centralised platform starts from one assumption: “you” are a row in its database. A phone number, a profile, a contact graph that belongs to it and that it can hand over. Konstruct starts from less. The server holds an account identifier, your public keys and a push token, and about the message itself only its size and the time it arrived. Exactly what routing ciphertext requires.

Любая централизованная платформа исходит из одного допущения: «вы» — это строка в её базе данных. Номер телефона, профиль, граф контактов, который ей принадлежит и который она может передать. Konstruct начинает с меньшего. Сервер хранит идентификатор аккаунта, ваши публичные ключи и push-токен, а о самом сообщении — только размер и время. Ровно столько нужно, чтобы маршрутизировать шифротекст.

## home.identity.limit  ·  HTML allowed

> Cryptography cannot make you unobservable. Timing and IP correlation remain visible on the wire, and a sufficiently resourced adversary works at that layer, not this one. Even so, no component of our system is designed to accumulate your data.

Криптография не делает вас ненаблюдаемым. Корреляция по времени и IP остаётся видимой на проводе, и достаточно ресурсный противник работает на том уровне, а не на этом. Однако ни один компонент нашей системы не спроектирован, чтобы накапливать ваши данные.

## home.identity.title  ·  plain text

> Identity is a Construct

Идентичность — это конструкт

## home.meta.title  ·  plain text

> Konstruct - Privacy-First Secure Messenger with Post-Quantum Encryption

Konstruct — Мессенджер с постквантовым шифрованием

## home.more.roadmap  ·  plain text

> What is done and what is planned →

Что уже сделано и что в планах →

## home.more.technical  ·  plain text

> How this is built — transport, crypto stack, what the server sees →

Как это устроено — транспорт, криптография, что видит сервер →

## home.roadmap.decentralization-roadmap  ·  plain text

> Decentralization Roadmap

Дорожная карта децентрализации

## home.roadmap.development-roadmap  ·  plain text

> Development Roadmap

Дорожная карта

## home.roadmap.other-planned-work  ·  plain text

> Other Planned Work

Прочие планы

## home.roadmap.t10  ·  plain text

> video calls · Privacy Pass token enforcement (anti-spam on the always-on sealed-sender path) · desktop applications for Windows, Linux · formal verification (Kani).

видеозвонки · enforcement Privacy Pass токенов (анти-спам на пути с постоянной защитой отправителя) · десктоп-приложения для Windows, Linux · формальная верификация (Kani).

## home.roadmap.t11  ·  HTML allowed

> <strong>Honest current status:</strong> alpha. iOS via TestFlight only (<a href="https://testflight.apple.com/join/NH3WssFh">join the beta</a>); no public App Store release yet. macOS Desktop client is in active development, no build available yet. Single trusted server (no federation). Censorship-resistant transport ships and is on by default, but we do not publish where it currently does or does not get through. Not recommended for adversarial threat models until the first external audit completes.

<strong>Текущий статус:</strong> альфа. iOS только через TestFlight (<a href="https://testflight.apple.com/join/NH3WssFh">присоединиться к бете</a>), публичного релиза в App Store пока нет. Десктопный клиент macOS в активной разработке, сборки пока нет. Один доверенный сервер (без федерации). Транспорт с устойчивостью к цензуре поставляется и включён по умолчанию, но где он сейчас проходит, а где нет, мы не публикуем. Не рекомендуется для враждебных моделей угроз, пока не завершён первый внешний аудит.

## home.roadmap.t2  ·  HTML allowed

> <strong>Done (H1 2026):</strong> gRPC/Protobuf · live <strong>gRPC bidi MessageStream over QUIC</strong> (HTTP/2 fallback; intercontinental production validation) · X3DH + Double Ratchet · PQXDH with ML-KEM-768 · session healing · WebRTC voice calls with E2EE signaling · iOS TestFlight beta · censorship-resistant transport · always-on Stealth (sealed sender) for eligible traffic.

<strong>Сделано (H1 2026):</strong> gRPC/Protobuf · живой <strong>gRPC bidi MessageStream поверх QUIC</strong> (фолбэк HTTP/2; проверка на межконтинентальных связях в бою) · X3DH + Double Ratchet · PQXDH с ML-KEM-768 · восстановление сессий · WebRTC аудиозвонки с E2EE-сигналингом · iOS TestFlight бета · транспорт с устойчивостью к цензуре · постоянно включённая защита отправителя для подходящего трафика.

## home.roadmap.t3  ·  HTML allowed

> <strong>In progress:</strong> macOS Desktop client (iOS-direct crypto path, no public build yet) · Android client (currently Phase 0 — Rust core builds, Kotlin wrapper TBD) · BIP39 / SLIP-39 social recovery · MLS group chats (RFC 9420) · first external security audit · hybrid PQ signatures (ML-DSA-65) — crypto core and server storage / verification implemented, client-side orchestration (identity generation, key rotation) not yet wired into the shared core.

<strong>В работе:</strong> десктопный клиент macOS (крипто-путь как на iOS, публичной сборки пока нет) · Android-клиент (сейчас Phase 0 — ядро на Rust собирается, Kotlin-обёртка впереди) · социальное восстановление BIP39 / SLIP-39 · групповые чаты MLS (RFC 9420) · первый внешний аудит безопасности · гибридные PQ-подписи (ML-DSA-65) — криптоядро и серверное хранение/верификация реализованы, клиентская оркестрация (генерация идентичности, ротация ключей) ещё не заведена в общее ядро.

## home.roadmap.t5  ·  HTML allowed

> <strong>Decentralisation, in order:</strong> the standalone <code>construct-relay</code> binary (store-and-forward for server-to-server messages, origin signatures verified, two containers on a small VPS) · a DHT for peer discovery and offline storage · direct peer-to-peer delivery with relay fallback · public seed nodes, spam resistance and MLS groups over the decentralised transport. The relay binary exists; everything after it is 2027 and later.

<strong>Децентрализация, по порядку:</strong> отдельный бинарник <code>construct-relay</code> (store-and-forward для сообщений между серверами, проверка подписи источника, два контейнера на небольшом VPS) · DHT для поиска пиров и офлайн-хранения · прямая доставка между устройствами с откатом на реле · публичные seed-узлы, устойчивость к спаму и MLS-группы поверх децентрализованного транспорта. Бинарник реле есть; всё, что после него, — 2027 год и позже.

## home.support.convenient-but-not-private  ·  plain text

> convenient but not private

удобно, но не приватно

## home.support.privacy-policy  ·  plain text

> Privacy Policy

Политика конфиденциальности

## home.support.recommended-private  ·  plain text

> recommended, private

рекомендуется, приватно

## home.support.support-the-project  ·  plain text

> Support the Project

Поддержать проект

## home.support.t2  ·  HTML allowed

> No ads, data resale or telemetry — Konstruct runs on voluntary donations. If you want the messaging core to stay free and independent, a donation directly funds development and the server. Prefer <strong>Monero</strong> if you value privacy: unlike Bitcoin, its chain is not public, so your donation isn't linkable and the balance isn't visible.

Без рекламы, перепродажи данных и телеметрии — Konstruct живёт на добровольных донатах. Если хотите, чтобы ядро мессенджера оставалось бесплатным и независимым, донат напрямую идёт на разработку и сервер. Если цените приватность — предпочтите <strong>Monero</strong>: в отличие от биткоина его цепочка не публична, донат нельзя связать, а баланс не виден.

## home.support.t5  ·  plain text

> Note: fiat payments aren't anonymous — the processor knows who you are. Use Monero for a private donation.

Учтите: фиатные платежи не анонимны — платёжный сервис знает, кто вы. Для приватного доната используй Monero.

## home.support.t6  ·  plain text

> Security tip: these addresses are also published, PGP-signed, in the project repository — cross-check them there before sending, in case this page is ever tampered with. Signing key fingerprint:

Совет по безопасности: эти адреса также опубликованы и PGP-подписаны в репозитории проекта — сверь их там перед отправкой на случай, если эту страницу подменят. Отпечаток ключа подписи:

## home.support.t7  ·  HTML allowed

> Built with Rust, Swift, and a commitment to privacy.<br /> Open source (MPL-2.0 apps · AGPL-3.0 server)

Создан на Rust, Swift и принципах приватности.<br /> Открытый код (MPL-2.0 приложения · AGPL-3.0 сервер)

## home.support.t8  ·  plain text

> © 2026 Konstruct. Identity is a construct.

© 2026 Konstruct. Идентичность — это конструкт.

## home.sys-online  ·  plain text

> SYS::ONLINE

SYS::ONLINE

## home.t4  ·  plain text

> An account tied to nothing in the real world. No phone number, no email, no name — not at sign-up, not in the database. End-to-end encryption is ordinary now. An account with nothing behind it is not.

Аккаунт, не связанный ни с одним идентификатором реального мира. Ни номера, ни почты, ни имени — ни при регистрации, ни в базе. Сквозным шифрованием сегодня никого не удивишь; аккаунтом, за которым ничего не стоит, — можно.

## home.t4b  ·  plain text

> Signal Protocol · post-quantum key agreement (ML-KEM-768) · gRPC stream over QUIC · sealed sender always on

Signal Protocol · постквантовое согласование ключей (ML-KEM-768) · gRPC-поток поверх QUIC · защита отправителя всегда включена

## home.t4c  ·  plain text

> A second channel, not a replacement for your main messenger. Today that means one-to-one chats and calls on iOS, one server, an early build. No groups, no channels, no sync between your devices — a second channel does not need them.

Второй канал связи, а не замена основному. Сегодня это переписка и звонки один на один на iOS, один сервер, ранняя стадия. Ни групп, ни каналов, ни синхронизации между вашими устройствами — второму каналу они не нужны.

## home.telemetry.no-telemetry-not-anonymised-absent  ·  plain text

> No Telemetry. Not Anonymised — Absent.

Никакой телеметрии. Даже «обезличенной».

## home.telemetry.t2  ·  HTML allowed

> Konstruct collects no analytics, no usage metrics, no behavioural events, no crash reports and no advertising identifiers. There are no third-party SDKs — no Firebase, no Crashlytics, no Sentry — and no ATT prompt or SKAdNetwork. Release builds write no logs to disk: when logs are needed to fix a bug, you send them yourself with a button in a beta build. One thing we do not control: while the beta runs on TestFlight, Apple reports its own standard testing metrics to us — install date, build version, session and crash counts. That is Apple's, not ours, and it ends with the App Store release. To route a message the server does hold a small fixed set of metadata — recipient, time, size, your public keys, push token — and sealed sender takes the sender out of the envelope as well. What that does not solve, timing and IP correlation, is written down in the <a href="/privacy">Privacy Policy</a>.

Konstruct не собирает аналитику, метрики использования, поведенческие события, отчёты о крашах и рекламные идентификаторы. Сторонних SDK нет — ни Firebase, ни Crashlytics, ни Sentry, — как нет ATT-запроса и SKAdNetwork. Релизные сборки не пишут никаких логов. Одного мы не контролируем: пока бета идёт в TestFlight, Apple отдаёт нам свои стандартные метрики тестирования — дату установки, версию сборки, число сессий и крашей. Это метрики Apple, не наши, и они закончатся с релизом в App Store. Для маршрутизации сервер хранит только небольшой фиксированный набор метаданных — получатель, время, размер, ваши публичные ключи, push-токен, — а защита отправителя убирает из конверта и его самого. Чего это не решает, корреляцию по времени и IP, мы описали в <a href="/privacy">Политике конфиденциальности</a>.

## home.why.counter  ·  HTML allowed

> <strong>The caveat: no external audit yet.</strong> Everything above is our own reading of our own code. It has not been checked by anyone outside the project, and until it has, treat the four properties as claims we are prepared to defend rather than as findings. There is also one server: if it is unreachable, nothing is delivered — there is no second route today.

<strong>Оговорка: внешнего аудита не было.</strong> Всё, что выше, — это наше собственное прочтение нашего же кода. Никто вне проекта его не проверял, и пока это так, считайте четыре свойства заявлениями, которые мы готовы защищать, а не результатами проверки. И сервер один: если он недоступен, ничего не доставляется — второго маршрута сегодня нет.

## home.why.id.answer  ·  HTML allowed

> <strong>An account is a keypair.</strong> No phone number, no email, no required username, and discovery is off by default. A subpoena to a carrier reaches nothing, because no carrier is in the loop.

<strong>Аккаунт — пара ключей.</strong> Ни номера телефона, ни почты, ни обязательного имени; обнаружение по умолчанию выключено. Запрос оператору связи ничего не даёт: оператора в цепочке нет.

## home.why.lead  ·  plain text

> And an honest caveat.

И одна оговорка.

## home.why.note.opaque  ·  HTML allowed

> An <strong>opaque identifier</strong> is a string that says nothing about you — characters assigned when the account was created.

<strong>Непрозрачный идентификатор</strong> — это строка, которая ничего о вас не сообщает: набор символов, выданный при создании аккаунта.

## home.why.note.sender  ·  HTML allowed

> <strong>Sealed sender</strong> means a message travels with no mark of who wrote it. Only the recipient can open that; the server cannot. In the app it is the “stealth” switch.

<strong>Защита отправителя</strong> — сообщение уходит без пометки о том, кто его написал. Раскрыть её может только получатель, сервер — нет. В приложении это переключатель «стелс».

## home.why.pq.answer  ·  HTML allowed

> <strong>Post-quantum, already in the protocol.</strong> ML-KEM-768 is encapsulated to the recipient's Kyber prekey at session setup (PQXDH). The first message of a conversation is classical-only by design; everything after it is not.

<strong>Постквантовость уже в протоколе.</strong> ML-KEM-768 инкапсулируется в Kyber-префикс получателя при установке сессии (PQXDH). Первое сообщение разговора по замыслу классическое, всё последующее — нет.

## home.why.sealed.answer  ·  HTML allowed

> <strong>The sender is not in the envelope.</strong> Sealed sender<a class="fn-marker" href="#fn-sender" aria-label="What sealed sender means">*</a> is unconditional for ordinary traffic. To route a message the server has an opaque account id<a class="fn-marker" href="#fn-opaque" aria-label="What an opaque identifier is">**</a>, a size and a time.

<strong>Отправителя нет в конверте.</strong> Защита отправителя<a class="fn-marker" href="#fn-sender" aria-label="Что такое защита отправителя">*</a> безусловна для обычного трафика. Для доставки у сервера есть непрозрачный идентификатор аккаунта<a class="fn-marker" href="#fn-opaque" aria-label="Что такое непрозрачный идентификатор">**</a>, размер и время.

## home.why.title  ·  plain text

> Four properties

Четыре свойства

## home.why.transport.answer  ·  HTML allowed

> gRPC bidirectional over QUIC with HTTP/2 fallback — one long-lived stream that survives a change of network without a new handshake.

Двунаправленный gRPC поверх QUIC с откатом на HTTP/2 — один долгоживущий стрим, переживающий смену сети без нового хендшейка.
