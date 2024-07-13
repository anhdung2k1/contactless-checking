#!/bin/sh

# Use sed to replace placeholders with actual values or default values
sed -i -e "s|\$MODEL_URL|${MODEL_URL}|g" /usr/share/nginx/html/config.template.js
sed -i -e "s|\$HOST_IP|${HOST_IP}|g" /usr/share/nginx/html/config.template.js

# Rename the modified file to config.js
mv /usr/share/nginx/html/config.template.js /usr/share/nginx/html/config.js

# Execute the command passed to the container
exec "$@"