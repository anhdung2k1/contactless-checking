{{/* vim: set filetype=mustache: */}}

{{/*
Create a map from ".Values.global" with defaults if missing in values file.
*/}}
{{ define "ck-mysql.global" }}
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
Expand the name of the chart
*/}}
{{- define "ck-mysql.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Selector labels.
*/}}
{{- define "ck-mysql.selectorLabels" -}}
component: {{ .Values.server.mysqlServer.name | quote }}
app: {{ template "ck-mysql.name" . }}
release: {{ .Release.Name | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
{{- end }}

{{/*
Define product-info
*/}}
{{- define "ck-mysql.product-info" }}
    mysql.com/product-name: {{ (fromYaml (.Files.Get "ck-product-info.yaml")).productName | quote }}
    mysql.com/product-revision: {{regexReplaceAll "(.*)[+].*" .Chart.Version "${1}" }}
{{- end }}

{{/*
Define annotations
*/}}
{{- define "ck-mysql.annotations" -}}
    {{- $g := fromJson (include "ck-mysql.global" .) -}}
    {{- $productInfo := include "ck-mysql.product-info" . | fromYaml -}}
    {{- $global := $g.annotations -}}
    {{- $service := .Values.annotations -}}
    {{- include "ck-mysql.mergeAnnotations" (dict "location" .Template.Name "sources" (list $productInfo $global $service)) | trim }}
{{- end }}

{{/*
Create version
*/}}
{{- define "ck-mysql.version" -}}
{{- printf "%s" .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Define imagePath
*/}}
{{- define "ck-mysql.imagePath" -}}
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
{{- define "ck-mysql.imagePullPolicy" -}}
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
{{- define "ck-mysql.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Static labels
*/}}
{{- define "ck-mysql.static-labels" -}}
{{- $top := index . 0 }}
{{- $name := index . 1 }}
app.kubernetes.io/name: {{ $name }}
app.kubernetes.io/version: {{ template "ck-mysql.version" $top }}
chart: {{ template "ck-mysql.chart" $top }}
heritage: {{ $top.Release.Service | quote }}
{{- end -}}

{{/*
Merged labels for common
*/}}
{{- define "ck-mysql.labels" -}}
    {{- $g := fromJson (include "ck-mysql.global" .) -}}
    {{- $selector := include "ck-mysql.selectorLabels" . | fromYaml -}}
    {{- $name := (include "ck-mysql.name" .) }}
    {{- $static := include "ck-mysql.static-labels" (list . $name) | fromYaml -}}
    {{- $global := $g.label -}}
    {{- $service := .Values.labels -}}
    {{- include "ck-mysql.mergeLabels" (dict "location" .Template.Name "sources" (list $selector $static $global $service)) | trim }}
{{- end -}}

{{/*
Define fsGroup
*/}}
{{- define "ck-mysql.fsGroup.coordinated" -}}
    {{- $g := fromJson (include "ck-mysql.global" .) -}}
    {{- if $g -}}
        {{- if $g.fsGroup -}}
            {{- if $g.fsGroup.manual -}}
                {{ $g.fsGroup.manual }}
            {{- else -}}
                {{- if $g.fsGroup.namespace -}}
                    {{- if eq $g.fsGroup.namespace true -}}
                        # The namespace default value is used
                    {{- else -}}
                        10000
                    {{- end -}}
                {{- else -}}
                    10000
                {{- end -}}
            {{- end -}}
            {{- else -}}
                10000
            {{- end -}}
        {{- else -}}
            10000
    {{- end -}}
{{- end -}}

{{/*
Define podSeccompProfile
*/}}
{{- define "ck-mysql.podSeccompProfile" -}}
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
{{- define "ck-mysql.supplementalGroups" -}}
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
{{- $g := fromJson (include "ck-mysql.global" .) -}}
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
{{- $g := fromJson (include "ck-mysql.global" .) -}}
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
