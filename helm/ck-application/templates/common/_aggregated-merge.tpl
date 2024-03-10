{{- define "ck-application.aggregatedMerge" -}}
{{- $merged := dict -}}
{{- $context := .context -}}
{{- $location := .location -}}

{{- range $sourceData := .sources -}}
  {{- range $key, $value := $sourceData -}}

    {{- /* FAIL: when the input is not string. */ -}}
    {{- if not (kindIs "string" $value) -}}
      {{- $problem := printf "Failed to merge keys for \"%s\" in \"%s\": invalid type" $context $location -}}
      {{- $details := printf "in \"%s\": \"%s\"." $key $value -}}
      {{- $reason := printf "The merge function only accepts strings as input." -}}
      {{- $solution := "To proceed, please pass the value as a string and try again." -}}
      {{- printf "%s %s %s %s" $problem $details $reason $solution | fail -}}
    {{- end -}}

    {{- if hasKey $merged $key -}}
      {{- $mergedValue := index $merged $key -}}

      {{- /* FAIL: when there are different values for a key. */ -}}
      {{- if ne $mergedValue $value -}}
        {{- $problem := printf "Failed to merge keys for \"%s\" in \"%s\": key duplication in" $context $location -}}
        {{- $details := printf "\"%s\": (\"%s\", \"%s\")." $key $mergedValue $value -}}
        {{- $reason := printf "The same key cannot have different values." -}}
        {{- $solution := "To proceed, please resolve the conflict and try again." -}}
        {{- printf "%s %s %s %s" $problem $details $reason $solution | fail -}}
      {{- end -}}
    {{- end -}}

    {{- $_ := set $merged $key $value -}}

  {{- end -}}
{{- end -}}

{{- range $key, $value := $merged }}
{{ $key }}: {{ $value | quote }}
{{- end -}}
{{- end}}

{{- define "ck-application.mergeAnnotations" -}}
    {{- include "ck-application.aggregatedMerge" (dict "context" "annotations" "location" .location "sources" .sources) }}
{{- end -}}

{{- define "ck-application.mergeLabels" -}}
    {{- include "ck-application.aggregatedMerge" (dict "context" "labels" "location" .location "sources" .sources) }}
{{- end -}}