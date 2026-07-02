#!/bin/sh
PORT="${PORT:-80}"
sed -i "s/listen 80;/listen ${PORT};/" /etc/nginx/conf.d/default.conf

# Default baked at build; override via Railway variable API_UPSTREAM
API_UPSTREAM="${API_UPSTREAM:-}"

if [ -n "$API_UPSTREAM" ]; then
  base=$(echo "$API_UPSTREAM" | sed 's:/*$::')
  host=$(echo "$base" | sed -e 's#^https://##' -e 's#^http://##' -e 's#/.*##' -e 's#:.*##')
  ssl=""
  if echo "$base" | grep -q '^https://'; then
    ssl="proxy_ssl_server_name on;
    proxy_ssl_verify off;"
  fi
  cat > /etc/nginx/conf.d/proxy.conf <<EOF
location /api/ {
    proxy_pass ${base};
    ${ssl}
    proxy_set_header Host ${host};
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_read_timeout 60s;
    proxy_buffering on;
    client_max_body_size 10m;
}

location /uploads/ {
    proxy_pass ${base};
    ${ssl}
    proxy_set_header Host ${host};
    proxy_read_timeout 60s;
    proxy_buffering on;
    client_max_body_size 10m;
}
EOF
  echo "nginx proxy -> ${base}"
else
  echo "# no API_UPSTREAM" > /etc/nginx/conf.d/proxy.conf
  echo "WARNING: API_UPSTREAM not set — /api and /uploads will 404 on miniapp host"
fi

exec nginx -g 'daemon off;'
