package com.example.authentication.service.implement;

import com.example.authentication.service.interfaces.JenkinsService;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.List;
import java.util.Map;

@Service
@Transactional(rollbackOn = Exception.class)
@RequiredArgsConstructor
@Slf4j
public class JenkinsServiceImpl implements JenkinsService {

    @Autowired
    private final RestTemplate restTemplate;

    @Override
    public String requestBuildWithParameters(Map<String, Object> params) {
        String jenkinsUrl = (String) params.get("jenkinsUrl");
        String jobName = (String) params.get("jobName");
        String userName = (String) params.get("userName");
        String apiToken = (String) params.get("apiToken");
        String[] variableKeys = ((List<String>) params.get("variableKey")).toArray(new String[0]);
        String[] variableValues = ((List<String>) params.get("variableValue")).toArray(new String[0]);

        // Construct the Jenkins URL
        UriComponentsBuilder uriBuilder = UriComponentsBuilder.fromHttpUrl(jenkinsUrl + "/job/" + jobName + "/buildWithParameters");

        // Add the variable parameters to the URL
        for (int i = 0; i < variableKeys.length; i++) {
            uriBuilder.queryParam(variableKeys[i], variableValues[i]);
        }

        String uri = uriBuilder.toUriString();

        log.info("Constructed Jenkins URL: {}", uri);

        // Set the headers for the request
        HttpHeaders headers = new HttpHeaders();
        headers.setBasicAuth(userName, apiToken);
        headers.setContentType(MediaType.APPLICATION_JSON);

        log.info("Headers: {}", headers);

        ResponseEntity<String> response = null;
        try {
            log.info("Sending request to Jenkins...");
            response = restTemplate.exchange(uri, HttpMethod.POST, new HttpEntity<>(headers), String.class);
            log.info("Received response from Jenkins with status code: {}", response.getStatusCode());
        } catch (Exception e) {
            log.error("Error occurred while sending request to Jenkins: {}", e.getMessage());
        }

        // Log response body
        if (response != null) {
            String responseBody = response.getBody();
            if (responseBody == null) {
                responseBody = "{\"status\":\"" + response.getStatusCode() + "\", \"message\":\"Build triggered successfully, but no response body returned.\"}";
            }
            log.info("Response body: {}", responseBody);
            return responseBody;
        } else {
            log.error("Response is null");
            return "{\"status\":\"500\", \"message\":\"Failed to trigger build.\"}";
        }
    }
}
