{{- define "ck-client-containers" -}}
{{- $top := index . 0 -}}
{{- $externalIP := $top.Values.server.externalIP -}}
{{- $modelURL := printf "https://%s:%s" $externalIP $top.Values.server.faceModel.port -}}
{{- $hostIP := printf "https://%s:%s" $externalIP $top.Values.server.authentication.port -}}
- name: {{ $top.Values.server.faceClient.name }}
  image: {{ include "ck-application.imagePath" (merge (dict "imageName" "ck-face-client") $top) }}
  imagePullPolicy: {{ include "ck-application.imagePullPolicy" $top }}
  env:
    - name: MODEL_URL
      value: {{ $modelURL }}
    - name: HOST_IP
      value: {{ $hostIP }}
  ports:
    - name: http-client-svc
      containerPort: {{ $top.Values.server.faceClient.httpPort }}
    - name: tls-client-svc
      containerPort: {{ $top.Values.server.faceClient.tlsPort }}
  resources:
    {{- include "ck-application.resources" (index $top.Values "resources" "face-client") | indent 2 }}
{{- end -}}