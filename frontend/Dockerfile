# Этап 1: Сборка приложения
FROM node:18 AS build

# Задаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем все файлы приложения в контейнер
COPY . .

# Собираем приложение
RUN npm run build

# Этап 2: Создание минимального образа для продакшн
FROM nginx:stable-alpine

# Копируем собранное приложение из предыдущего этапа
COPY --from=build /app/build /usr/share/nginx/html
COPY --from=build /app/nginx.conf /etc/nginx/conf.d/default.conf

# Копируем файл конфигурации Nginx (если требуется)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]