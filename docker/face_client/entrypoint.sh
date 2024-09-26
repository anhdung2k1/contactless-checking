#!/bin/sh

# Replace the MODEL_URL with the new value
sed -i -e "s|MODEL_URL:.*|MODEL_URL: '${MODEL_URL}',|g" /usr/share/nginx/html/js/actions/config.js

# Replace the HOST_IP with the new value
sed -i -e "s|HOST_IP:.*|HOST_IP: '${HOST_IP}',|g" /usr/share/nginx/html/js/actions/config.js

# Execute the command passed to the container
exec "$@"