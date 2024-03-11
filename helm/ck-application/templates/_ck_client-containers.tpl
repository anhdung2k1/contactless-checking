{{- define "ck-client-container" -}}
{{- $top := index . 0 -}}
- name: {{ $top.Values.server.client.name }}
  image: {{ template "ck-application.imagePath" (merge (dict "imageName" "ck-client") $top) }}
  imagePullPolicy: {{ template "ck-application.imagePullPolicy" $top }}
  ports:
    - containerPort: {{ $top.Values.server.client.port }}
  env:
  - name: SERVER_HOST
    value: {{ template "ck-server.name" $top }}
  - name: SERVER_PORT
    value: {{ $top.Values.server.socketServer.port | quote }}
{{- end -}}