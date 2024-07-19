{{- define "ck-auth-containers" -}}
{{- $top := index . 0 -}}
- name: {{ $top.Values.server.authentication.name }}
  image: {{ template "ck-application.imagePath" (merge (dict "imageName" "ck-authentication") $top) }}
  imagePullPolicy: {{ template "ck-application.imagePullPolicy" $top }}
  ports:
    - name: https-auth-svc
      containerPort: {{ $top.Values.server.authentication.port }}
  resources:
{{- include "ck-application.resources" (index $top.Values "resources" "authentication") | indent 2 }}
  env:
  - name: DB_HOST
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-mysql.name" $top }}-secret
        key: {{ template "ck-mysql.name" $top }}-host
  - name: DB_NAME
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-mysql.name" $top }}-secret
        key: {{ template "ck-mysql.name" $top }}-dbName
  - name: DB_USERNAME
  {{- if not (eq ((include "ck-mysql.password" $top) | b64dec) "root") }}
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-mysql.name" $top }}-secret
        key: {{ template "ck-mysql.name" $top }}-user
  {{- else }}
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-mysql.name" $top }}-secret
        key: {{ template "ck-mysql.name" $top }}-root-password
  {{- end }}
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-mysql.name" $top }}-secret
        key: {{ template "ck-mysql.name" $top }}-password
{{- end -}}