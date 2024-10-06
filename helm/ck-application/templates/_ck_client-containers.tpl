{{- define "ck-client-containers" -}}
{{- $top := index . 0 -}}
- name: {{ $top.Values.server.faceClient.name }}
  image: {{ include "ck-application.imagePath" (merge (dict "imageName" "ck-face-client") $top) }}
  imagePullPolicy: {{ include "ck-application.imagePullPolicy" $top }}
  env:
  # The fetch client used external IP from LoadBalancer/NodePort or Ingress. Not working with ClusterIP
  - name: MODEL_URL
    {{- if $top.Values.ingress.enabled }}
    value: http://{{ include "ck-application.ingressPath" (list $top (include "ck-server.name" $top )) }}
    {{- else }}
    value: http://{{ $top.Values.server.nodeIP }}:{{ $top.Values.server.faceModel.httpNodePort }}
    {{- end }}
  - name: HOST_IP
    {{- if $top.Values.ingress.enabled }}
    value: http://{{ include "ck-application.ingressPath" (list $top (include "ck-authentication.name" $top )) }}
    {{- else }}
    value: http://{{ $top.Values.server.nodeIP }}:{{ $top.Values.server.authentication.httpNodePort }}
    {{- end }}
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