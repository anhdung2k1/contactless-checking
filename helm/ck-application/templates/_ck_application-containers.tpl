{{- define "ck-application-containers" -}}
{{- $top := index . 0 -}}
- name: {{ $top.Values.server.authentication.name }}
  image: {{ template "ck-application.imagePath" (merge (dict "imageName" "ck-authentication") $top) }}
  imagePullPolicy: {{ template "ck-application.imagePullPolicy" $top }}
  ports:
    - containerPort: {{ $top.Values.server.authentication.port }}
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
- name: {{ $top.Values.server.faceModel.name }}
  image: {{ template "ck-application.imagePath" (merge (dict "imageName" "ck-face-model") $top) }}
  imagePullPolicy: {{ template "ck-application.imagePullPolicy" $top }}
  ports:
    - containerPort: {{ $top.Values.server.faceModel.port }}
  resources:
{{- include "ck-application.resources" (index $top.Values "resources" "face-model") | indent 2 }}
  env:
  - name: AWS_ACCESS_KEY_ID
    value: {{ $top.Values.aws.key }}
  - name: AWS_SECRET_ACCESS_KEY
    value: {{ $top.Values.aws.secret }}
  - name: AWS_DEFAULT_REGION
    value: {{ $top.Values.aws.region }}
{{- end -}}