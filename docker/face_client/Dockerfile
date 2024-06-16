FROM nginx:latest

COPY --chmod=0755 --chown=0:0 face_client/* /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]