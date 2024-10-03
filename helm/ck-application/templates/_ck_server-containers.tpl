{{- define "ck-server-containers" -}}
{{- $top := index . 0 -}}
- name: {{ $top.Values.server.faceModel.name }}
  image: {{ template "ck-application.imagePath" (merge (dict "imageName" "ck-face-model") $top) }}
  imagePullPolicy: {{ template "ck-application.imagePullPolicy" $top }}
  ports:
    - name: http-server-svc
      containerPort: {{ $top.Values.server.faceModel.port }}
  resources:
{{- include "ck-application.resources" (index $top.Values "resources" "face-model") | indent 2 }}
  env:
  - name: AWS_ACCESS_KEY_ID
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-authentication.name" $top }}-secret
        key: {{ template "ck-authentication.name" $top }}-aws-key
  - name: AWS_SECRET_ACCESS_KEY
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-authentication.name" $top }}-secret
        key: {{ template "ck-authentication.name" $top }}-aws-secret
  - name: AWS_DEFAULT_REGION
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-authentication.name" $top }}-secret
        key: {{ template "ck-authentication.name" $top }}-aws-region
  volumeMounts:
  - name: {{ template "ck-server.name" $top }}-persistent-storage
    mountPath: /app/build
volumes:
- name: {{ template "ck-server.name" $top }}-persistent-storage
  persistentVolumeClaim:
    claimName: {{ template "ck-server.name" $top }}-pv-claim
{{- end -}}