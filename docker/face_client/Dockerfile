FROM nginx:latest

# Set environment variables
ENV MODEL_URL=http://localhost:5000
ENV HOST_IP=http://localhost:8080

COPY --chmod=0755 --chown=0:0 face_client/ /usr/share/nginx/html
COPY --chmod=0755 --chown=0:0 entrypoint.sh /entrypoint.sh

EXPOSE 80
EXPOSE 443

ARG COMMIT
ARG APP_VERSION
ARG BUILD_TIME

LABEL \
    ck.app.commit=$COMMIT \
    ck.app.version=$APP_VERSION \
    ck.image.title="CK API Server" \
    ck.image.created="$BUILD_TIME"

ARG USER_ID
RUN echo "${USER_ID}:x:${USER_ID}:${USER_ID}:Identity for ck-application-server:/nonexistent:/bin/false" >> /etc/passwd && \
    echo "${USER_ID}:!::0:::::" >> /etc/shadow

USER ${USER_ID}

ENTRYPOINT ["/entrypoint.sh"]

CMD ["nginx", "-g", "daemon off;"]