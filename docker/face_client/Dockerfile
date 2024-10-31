FROM nginx:latest

# Set environment variables
ENV MODEL_URL=http://localhost:5000
ENV HOST_IP=http://localhost:8080

COPY --chmod=0755 --chown=0:0 face_client/ /usr/share/nginx/html
COPY --chmod=0755 --chown=0:0 entrypoint.sh /entrypoint.sh

ARG COMMIT
ARG APP_VERSION
ARG BUILD_TIME

LABEL \
    ck.app.commit=$COMMIT \
    ck.app.version=$APP_VERSION \
    ck.image.title="CK API Client" \
    ck.image.created="$BUILD_TIME"

EXPOSE 9080

ENTRYPOINT ["/entrypoint.sh"]

CMD ["nginx", "-g", "daemon off;"]