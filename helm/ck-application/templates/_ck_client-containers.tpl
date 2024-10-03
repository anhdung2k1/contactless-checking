{{- define "ck-client-containers" -}}
{{- $top := index . 0 -}}
- name: {{ $top.Values.server.faceClient.name }}
  image: {{ include "ck-application.imagePath" (merge (dict "imageName" "ck-face-client") $top) }}
  imagePullPolicy: {{ include "ck-application.imagePullPolicy" $top }}
  env:
  # Refer to client initContainer
  - name: MODEL_URL
    valueFrom:
      configMapKeyRef:
        name: service-ip-config
        key: server-service-url
  - name: HOST_IP
    valueFrom:
      configMapKeyRef:
        name: service-ip-config
        key: auth-service-url
  ports:
    - name: http-client-svc
      containerPort: {{ $top.Values.server.faceClient.httpPort }}
  resources:
{{- include "ck-application.resources" (index $top.Values "resources" "face-client") | indent 2 }}
  volumeMounts:
  - name: nginx-conf
    mountPath: /etc/nginx/conf.d/
volumes:
- name: nginx-conf
  configMap:
    name: {{ template "ck-client.name" $top }}-configmap
    items:
      - key: default.conf
        path: default.conf
{{- end -}}