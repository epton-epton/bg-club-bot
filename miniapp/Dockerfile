FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_API_URL=https://bgclub-api-production.up.railway.app
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

FROM nginx:alpine

ARG API_UPSTREAM=https://bgclub-api-production.up.railway.app
ENV API_UPSTREAM=$API_UPSTREAM

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh && rm -f /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["/docker-entrypoint.sh"]
