FROM nginx:latest

# Set environment variables
ENV MODEL_URL=http://localhost:5000
ENV HOST_IP=http://localhost:8080

COPY --chmod=0755 --chown=0:0 ssl/ /usr/share/nginx/ssl/
COPY --chmod=0755 --chown=0:0 face_client/* /usr/share/nginx/html
COPY --chmod=0755 --chown=0:0 default.conf /etc/nginx/conf.d/
COPY --chmod=0755 --chown=0:0 entrypoint.sh /entrypoint.sh

EXPOSE 80
EXPOSE 443

ENTRYPOINT ["/entrypoint.sh"]

CMD ["nginx", "-g", "daemon off;"]