#!/bin/sh
PORT="${PORT:-80}"
sed -i "s/listen 80;/listen ${PORT};/" /etc/nginx/conf.d/default.conf

if [ -n "$API_UPSTREAM" ]; then
  base=$(echo "$API_UPSTREAM" | sed 's:/*$::')
  host=$(echo "$base" | sed -e 's#^https://##' -e 's#^http://##' -e 's#/.*##')
  cat > /etc/nginx/conf.d/proxy.conf <<EOF
location /api/ {
    proxy_pass ${base};
    proxy_ssl_server_name on;
    proxy_set_header Host ${host};
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
}

location /uploads/ {
    proxy_pass ${base};
    proxy_ssl_server_name on;
    proxy_set_header Host ${host};
}
EOF
else
  echo "# no API_UPSTREAM" > /etc/nginx/conf.d/proxy.conf
fi

exec nginx -g 'daemon off;'
