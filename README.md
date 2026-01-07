# Konstruct Landing Page

Лендинг для Konstruct Messenger, размещенный на konstruct.cc

## Структура файлов

```
construct-landing/
├── index.html                          # Главная страница лендинга
├── contact.html                        # Страница для обработки контактных ссылок
├── .well-known/
│   └── apple-app-site-association     # Файл для Universal Links (iOS)
├── nginx.conf                          # Пример конфигурации Nginx
├── .htaccess                           # Конфигурация для Apache
└── README.md                           # Этот файл
```

## Настройка контактных ссылок

Ссылки вида `https://konstruct.cc/c/{userId}?username={username}` должны обрабатываться специальной страницей.

### Для Vercel (текущий хостинг)

Файл `vercel.json` уже настроен и автоматически обработает:
- Редирект `/c/{userId}` на `/contact.html?userId={userId}`
- Правильные заголовки для `apple-app-site-association`

После деплоя на Vercel все должно работать автоматически!

### Вариант 1: Nginx

Добавьте в конфигурацию вашего сервера (см. `nginx.conf`):

```nginx
location ~ ^/c/([^/]+)$ {
    rewrite ^/c/(.+)$ /contact.html?userId=$1&$args last;
}

location /.well-known/apple-app-site-association {
    default_type application/json;
    add_header Content-Type application/json;
}
```

### Вариант 2: Apache

Используйте файл `.htaccess` (уже включен в проект):

```apache
RewriteRule ^c/([^/]+)$ /contact.html?userId=$1 [QSA,L]
```

### Вариант 3: Cloudflare Pages / Vercel / Netlify

Для статических хостингов создайте файл `_redirects` или используйте настройки платформы:

**Netlify (`_redirects`):**
```
/c/:userId /contact.html?userId=:userId&:splat 200
```

**Vercel (`vercel.json`):**
Файл уже создан в проекте! Он автоматически:
- Перенаправляет `/c/:userId` на `/contact.html?userId=:userId`
- Устанавливает правильные заголовки для `apple-app-site-association`

**Cloudflare Pages:**
Используйте функцию `_redirects` или настройте через dashboard.

## Universal Links (iOS)

Файл `.well-known/apple-app-site-association` должен быть доступен по адресу:
```
https://konstruct.cc/.well-known/apple-app-site-association
```

**Важно:**
- Файл должен отдаваться с Content-Type: `application/json`
- Не должен иметь расширение `.json`
- Должен быть доступен без редиректов
- Требуется HTTPS

## Проверка

1. **Проверьте HTML страницу:**
   ```
   https://konstruct.cc/c/22dc1f77-ea29-4bdd-9529-2939dc311348?username=max
   ```
   Должна открыться страница `contact.html` с кнопками.

2. **Проверьте Universal Links:**
   ```bash
   curl https://konstruct.cc/.well-known/apple-app-site-association
   ```
   Должен вернуть JSON без ошибок.

3. **На iOS устройстве:**
   - Откройте ссылку в Safari
   - Если приложение установлено, должно предложить открыть в приложении

## Деплой

После настройки сервера просто загрузите все файлы на ваш хостинг. Убедитесь, что:
- Файлы `.well-known/apple-app-site-association` доступен по HTTPS
- Настроены редиректы для путей `/c/{userId}`
- SSL сертификат валиден

