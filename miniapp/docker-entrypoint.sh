#!/bin/sh
set -e

PORT="${PORT:-80}"
UPSTREAM="${API_UPSTREAM:-https://bgclub-api-production.up.railway.app}"
UPSTREAM=$(echo "$UPSTREAM" | tr -d '\r' | sed 's:/*$::')
case "$UPSTREAM" in
  http://*|https://*) ;;
  *) UPSTREAM="https://$UPSTREAM" ;;
esac
HOST=$(echo "$UPSTREAM" | sed -e 's#^https://##' -e 's#^http://##' -e 's#/.*##' -e 's#:.*##')

cat > /etc/nginx/conf.d/default.conf <<EOF
server {
    listen ${PORT};
    root /usr/share/nginx/html;
    index index.html;
    client_max_body_size 10m;

    location /api/ {
        proxy_pass ${UPSTREAM};
        proxy_ssl_server_name on;
        proxy_set_header Host ${HOST};
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 60s;
    }

    location /uploads/ {
        proxy_pass ${UPSTREAM};
        proxy_ssl_server_name on;
        proxy_set_header Host ${HOST};
        proxy_read_timeout 60s;
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /assets/ {
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

echo "nginx listen=${PORT} proxy=${UPSTREAM}"
nginx -t
exec nginx -g 'daemon off;'
