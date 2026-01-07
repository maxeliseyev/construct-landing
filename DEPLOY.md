# Инструкция по деплою на Vercel

## Что было добавлено

1. ✅ `contact.html` - страница для обработки контактных ссылок (стилизована под дизайн лендинга)
2. ✅ `.well-known/apple-app-site-association` - файл для Universal Links (iOS)
3. ✅ `vercel.json` - конфигурация Vercel для обработки ссылок

## Деплой

### Автоматический деплой (если уже подключен Git)

Просто сделайте commit и push:
```bash
git add .
git commit -m "Add contact link handling"
git push
```

Vercel автоматически задеплоит изменения.

### Ручной деплой

1. Установите Vercel CLI (если еще не установлен):
   ```bash
   npm i -g vercel
   ```

2. Задеплойте:
   ```bash
   cd /Users/maximeliseyev/Code/construct-landing
   vercel
   ```

## Проверка после деплоя

1. **Проверьте контактную ссылку:**
   ```
   https://konstruct.cc/c/22dc1f77-ea29-4bdd-9529-2939dc311348?username=max
   ```
   Должна открыться страница `contact.html` с темным дизайном.

2. **Проверьте Universal Links:**
   ```bash
   curl https://konstruct.cc/.well-known/apple-app-site-association
   ```
   Должен вернуть JSON с правильным Content-Type.

3. **На iOS устройстве:**
   - Откройте ссылку в Safari
   - Если приложение установлено, должно предложить открыть в приложении

## Как это работает

- `vercel.json` настроен так, что все запросы к `/c/{userId}` автоматически перенаправляются на `/contact.html?userId={userId}`
- Query параметры (например, `?username=max`) сохраняются автоматически
- Файл `apple-app-site-association` обслуживается с правильными заголовками для iOS

## Если что-то не работает

1. Проверьте, что файл `vercel.json` находится в корне проекта
2. Убедитесь, что файл `.well-known/apple-app-site-association` задеплоен
3. Проверьте логи деплоя в Vercel Dashboard
4. Убедитесь, что домен `konstruct.cc` правильно настроен в Vercel

