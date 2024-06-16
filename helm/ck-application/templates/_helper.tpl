{{/* vim: set filetype=mustache: */}}

{{/*
Create a map from ".Values.global" with defaults if missing in values file.
*/}}
{{ define "ck-application.global" }}
    {{- $globalDefaults := dict "registry" (dict "url" "anhdung12399") -}}
    {{- $globalDefaults := merge $globalDefaults (dict "timezone" "UTC") -}}
    {{- $globalDefaults := merge $globalDefaults (dict "nodeSelector" (dict)) -}}
    {{ if .Values.global }}
        {{- mergeOverwrite $globalDefaults .Values.global | toJson -}}
    {{ else }}
        {{- $globalDefaults | toJson }}
    {{ end }}
{{ end }}

{{/*
Expand the name of the mysql chart
*/}}
{{- define "ck-mysql.name" -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- printf "%s-mysql" $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Expand the name of the authentication chart
*/}}
{{- define "ck-authentication.name" -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- printf "%s-authentication" $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Expand the name of the server chart
*/}}
{{- define "ck-server.name" -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- printf "%s-server" $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Expand the name of the server chart
*/}}
{{- define "ck-client.name" -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- printf "%s-client" $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Selector labels for mysql.
*/}}
{{- define "ck-mysql.selectorLabels" -}}
component: {{ .Values.server.mysqlServer.name | quote }}
app: {{ template "ck-mysql.name" . }}
release: {{ .Release.Name | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
{{- end }}

{{/*
Selector labels for authentication.
*/}}
{{- define "ck-authentication.selectorLabels" -}}
component: {{ .Values.server.authentication.name | quote }}
app: {{ template "ck-authentication.name" . }}
release: {{ .Release.Name | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
{{- end }}

{{/*
Selector labels for server.
*/}}
{{- define "ck-server.selectorLabels" -}}
component: {{ .Values.server.socketServer.name | quote }}
app: {{ template "ck-server.name" . }}
release: {{ .Release.Name | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
{{- end }}

{{/*
Selector labels for server.
*/}}
{{- define "ck-client.selectorLabels" -}}
component: {{ .Values.server.client.name | quote }}
app: {{ template "ck-client.name" . }}
release: {{ .Release.Name | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
{{- end }}

{{/*
Define product-info
*/}}
{{- define "ck-application.product-info" }}
    ck-application.com/product-name: {{ (fromYaml (.Files.Get "ck-product-info.yaml")).productName | quote }}
    ck-application.com/product-revision: {{regexReplaceAll "(.*)[+].*" .Chart.Version "${1}" }}
{{- end }}

{{/*
Define annotations
*/}}
{{- define "ck-application.annotations" -}}
    {{- $g := fromJson (include "ck-application.global" .) -}}
    {{- $productInfo := include "ck-application.product-info" . | fromYaml -}}
    {{- $global := $g.annotations -}}
    {{- $service := .Values.annotations -}}
    {{- include "ck-application.mergeAnnotations" (dict "location" .Template.Name "sources" (list $productInfo $global $service)) | trim }}
{{- end }}

{{/*
Create version
*/}}
{{- define "ck-application.version" -}}
{{- printf "%s" .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Define imagePath
*/}}
{{- define "ck-application.imagePath" -}}
    {{- $productInfo := fromYaml (.Files.Get "ck-product-info.yaml") -}}
    {{- $image := (get $productInfo.images .imageName) -}}
    {{- $registryUrl := $image.registry -}}
    {{- $name := $image.name -}}
    {{- $tag := $image.tag -}}
    {{- printf "%s/%s:%s" $registryUrl $name $tag -}}
{{- end -}}

{{/*
Create imagePullPolicy
*/}}
{{- define "ck-application.imagePullPolicy" -}}
    {{- $imagePullPolicy := .Values.imageCredentials.pullPolicy -}}
    {{- if .Values.global -}}
        {{- if .Values.global.registry -}}
            {{- if .Values.global.registry.imagePullPolicy -}}
                {{- $imagePullPolicy = .Values.global.registry.imagePullPolicy -}}
            {{- end -}}
        {{- end -}}
    {{- end -}}
    {{- print $imagePullPolicy -}}
{{- end -}}

{{/*
Create chart name and version as used bt chart label.
*/}}
{{- define "ck-application.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Static labels
*/}}
{{- define "ck-application.static-labels" -}}
{{- $top := index . 0 }}
{{- $name := index . 1 }}
app.kubernetes.io/name: {{ $name }}
app.kubernetes.io/version: {{ template "ck-application.version" $top }}
chart: {{ template "ck-application.chart" $top }}
heritage: {{ $top.Release.Service | quote }}
{{- end -}}

{{/*
Merged labels for common mysql
*/}}
{{- define "ck-mysql.labels" -}}
    {{- $g := fromJson (include "ck-application.global" .) -}}
    {{- $selector := (include "ck-mysql.selectorLabels" .) | fromYaml -}}
    {{- $name := (include "ck-mysql.name" .) }}
    {{- $static := include "ck-application.static-labels" (list . $name) | fromYaml -}}
    {{- $global := $g.label -}}
    {{- $service := .Values.labels -}}
    {{- include "ck-application.mergeLabels" (dict "location" .Template.Name "sources" (list $selector $static $global $service)) | trim }}
{{- end -}}

{{/*
Merged labels for common authentication
*/}}
{{- define "ck-authentication.labels" -}}
    {{- $g := fromJson (include "ck-application.global" .) -}}
    {{- $selector := (include "ck-authentication.selectorLabels" .) | fromYaml -}}
    {{- $name := (include "ck-authentication.name" .) }}
    {{- $static := include "ck-application.static-labels" (list . $name) | fromYaml -}}
    {{- $global := $g.label -}}
    {{- $service := .Values.labels -}}
    {{- include "ck-application.mergeLabels" (dict "location" .Template.Name "sources" (list $selector $static $global $service)) | trim }}
{{- end -}}

{{/*
Merged labels for common server
*/}}
{{- define "ck-server.labels" -}}
    {{- $g := fromJson (include "ck-application.global" .) -}}
    {{- $selector := include "ck-server.selectorLabels" . | fromYaml -}}
    {{- $name := (include "ck-server.name" .) }}
    {{- $static := include "ck-application.static-labels" (list . $name) | fromYaml -}}
    {{- $global := $g.label -}}
    {{- $service := .Values.labels -}}
    {{- include "ck-application.mergeLabels" (dict "location" .Template.Name "sources" (list $selector $static $global $service)) | trim }}
{{- end -}}

{{/*
Merged labels for common server
*/}}
{{- define "ck-client.labels" -}}
    {{- $g := fromJson (include "ck-application.global" .) -}}
    {{- $selector := include "ck-client.selectorLabels" . | fromYaml -}}
    {{- $name := (include "ck-client.name" .) }}
    {{- $static := include "ck-application.static-labels" (list . $name) | fromYaml -}}
    {{- $global := $g.label -}}
    {{- $service := .Values.labels -}}
    {{- include "ck-application.mergeLabels" (dict "location" .Template.Name "sources" (list $selector $static $global $service)) | trim }}
{{- end -}}

{{/*
Define fsGroup
*/}}
{{- define "ck-application.fsGroup.coordinated" -}}
    {{- $g := fromJson (include "ck-application.global" .) -}}
    {{- if $g -}}
        {{- if $g.fsGroup -}}
            {{- if $g.fsGroup.manual -}}
                {{ $g.fsGroup.manual }}
            {{- else -}}
                {{- if $g.fsGroup.namespace -}}
                    {{- if eq $g.fsGroup.namespace true -}}
                        # The namespace default value is used
                    {{- else -}}
                        1000
                    {{- end -}}
                {{- else -}}
                    1000
                {{- end -}}
            {{- end -}}
            {{- else -}}
                1000
            {{- end -}}
        {{- else -}}
            1000
    {{- end -}}
{{- end -}}

{{/*
Define podSeccompProfile
*/}}
{{- define "ck-application.podSeccompProfile" -}}
{{- if and .Values.seccompProfile .Values.seccompProfile.type }}
seccompProfile:
  type: {{ .Values.seccompProfile.type }}
  {{- if eq .Values.seccompProfile.type "Localhost" }}
  localhostProfile: {{ .Values.seccompProfile.localhostProfile }}
  {{- end }}
{{- end }}
{{- end }}

{{/*
Configuration of supplementalGroups IDs
*/}}
{{- define "ck-application.supplementalGroups" -}}
    {{- $globalGroups := list -}}
    {{- if .Values.global -}}
        {{- if .Values.global.podSecurityContext -}}
            {{- if .Values.global.podSecurityContext.supplementalGroups -}}
                {{- if kindIs "slice" .Values.global.podSecurityContext.supplementalGroups -}}
                    {{- $globalGroups = .Values.global.podSecurityContext.supplementalGroups -}}
                {{- else -}}
                    {{- printf "global.podSecurityContext.supplementalGroups, \"%s\", is not a list." .Values.global.podSecurityContext.supplementalGroups | fail -}}
                {{- end -}}
            {{- end -}}
        {{- end -}}
    {{- end -}}

    {{- $localGroups := list -}}
    {{- if .Values.podSecurityContext -}}
        {{- if .Values.podSecurityContext.supplementalGroups -}}
            {{- if kindIs "slice" .Values.podSecurityContext.supplementalGroups -}}
                {{- $localGroups = .Values.podSecurityContext.supplementalGroups -}}
            {{- else -}}
                {{- printf "podSecurityContext.supplementalGroups, \"%s\", is not a list." .Values.podSecurityContext.supplementalGroups | fail -}}
            {{- end -}}
        {{- end -}}
    {{- end -}}

    {{- $mergedGroups := list -}}
    {{- range (concat $globalGroups $localGroups | uniq) -}}
        {{- if ne (. | toString) "" -}}
            {{- $mergeGroups = (append $mergedGroups . ) -}}
        {{- end -}}
    {{- end -}}

    {{- if gt (len $mergedGroups) 0 -}}
        {{ print "supplementalGroups:" | nindent 8 }}
        {{- toYaml $mergedGroups | nindent 10 }}
    {{- end -}}
{{- end -}}

{{/*
Create serviceAccountName    
*/}}
{{- define "ck-mysql.serviceAccountName" -}}
{{- $g := fromJson (include "ck-application.global" .) -}}
{{- if $g }}
    {{- $securityPolicyflags := include "ck-mysql.securityPolicy" . | fromYaml -}}
    {{- $securityPolicyExists := get $securityPolicyflags "securityPolicyExists" -}}
    {{- $oldPolicyFlag := get $securityPolicyflags "oldPolicyFlag" -}}
    {{- if (eq "true" $securityPolicyExists) }}
        {{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
    {{- else if .Values.server.mysqlServer.serviceAccountName }}
        {{- print .Values.server.mysqlServer.serviceAccountName }}
    {{- end }}
{{- end }}
{{- end -}}

{{- define "ck-mysql.securityPolicy.rolekind" -}}
{{- .Values.global.securityPolicy.rolekind -}}
{{- end -}}

{{- define "ck-mysql.securityPolicy.rolename" -}}
{{- default "ck-mysql" ( index .Values.securityPolicy "ck-mysql" "rolename" ) -}}
{{- end -}}

{{/*
Define securityPolicy
*/}}
{{- define "ck-mysql.securityPolicy" -}}
{{- $securityPolicyExists := "false" -}}
{{- $oldPolicyFlag := "false" -}}
{{- $g := fromJson (include "ck-application.global" .) -}}
{{- if $g -}}
    {{- if $g.securityPolicy -}}
        {{- if $g.securityPolicy.rolekind -}}
            {{- if and (ne .Values.global.securityPolicy.rolekind "Role") (ne .Values.global.securityPolicy.rolekind "ClusterRole") -}}
                {{- printf "For global.security.rolekind is not set correctly." | fail -}}
            {{- end -}}
            {{- $securityPolicyExists = "true" -}}
            {{- else -}}
                {{- $securityPolicyExists = "false" -}}
            {{- end -}}
        {{- else if $g.security -}}
            {{- if $g.security.policyBinding -}}
                {{- if $g.security.policyBinding.create -}}
                    {{- $securityPolicyExists = "true" -}}
                    {{- $oldPolicyFlag = "true" -}}
                {{- end -}}
        {{- end -}}
    {{- end -}}
{{- end -}}
{{- dict "securityPolicyExists" $securityPolicyExists "oldPolicyFlag" $oldPolicyFlag | toJson -}}
{{- end -}}

{{/*
Define resources
*/}}
{{- define "ck-mysql.resources" -}}
{{- if .limits }}
  limits:
  {{- if .limits.cpu }}
    cpu: {{ .limits.cpu | quote }}
  {{- end -}}
  {{- if .limits.memory }}
    memory: {{ .limits.memory | quote }}
  {{- end -}}
{{- end -}}
{{- if .requests }}
  requests:
  {{- if .requests.cpu }}
    cpu: {{ .requests.cpu | quote }}
  {{- end -}}
  {{- if .requests.memory }}
    memory: {{ .requests.memory | quote }}
  {{- end -}}
{{- end -}}
{{- end -}}

{{- define "ck-mysql.password" -}}
{{- $pass := "root" | b64enc -}}
{{- if .Values.dbPass -}}
    {{- $pass := .Values.dbPass -}}
{{- end -}}
{{- print $pass -}}
{{- end -}}

{{/*
Create secret for mysql
*/}}
{{- define "ck-mysql.secrets" -}}
{{- $password := (include "ck-mysql.password" .) }}
data:
  {{ template "ck-mysql.name" . }}-root-password: {{- print "root" | b64enc | indent 2 }}
  {{ template "ck-mysql.name" . }}-password: {{- $password | indent 2 }}
  {{- if not (eq ($password | b64dec) "root") }}
    {{ template "ck-mysql.name" . }}-user: {{- $password | indent 2 }}
  {{- end }}
  {{ template "ck-mysql.name" . }}-host: {{- include "ck-mysql.name" . | b64enc | indent 2 }}
  {{ template "ck-mysql.name" . }}-dbName: {{- print "checking" | b64enc | indent 2 }}
{{- end -}}