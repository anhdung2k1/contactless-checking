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
import org.springframework.beans.factory.annotation.Value;

import java.util.List;
import java.util.Map;

@Service
@Transactional(rollbackOn = Exception.class)
@RequiredArgsConstructor
@Slf4j
public class JenkinsServiceImpl implements JenkinsService {

    @Value("${cloud.aws.credentials.access-key}")
    private String accessKey;

    @Value("${cloud.aws.credentials.secret-key}")
    private String accessSecret;

    @Autowired
    private final RestTemplate restTemplate;

    @Override
    public String requestBuildWithParameters(Map<String, Object> params) {
        String jenkinsUrl = (String) params.get("jenkinsUrl");
        String jobName = (String) params.get("jobName");
        String userName = (String) params.get("userName");
        String apiToken = (String) params.get("apiToken");
        List<String> variableKeys = (List<String>) params.get("variableKey");
        List<String> variableValues = (List<String>) params.get("variableValue");

        // Add AWS credentials
        variableKeys.add("AWS_ACCESS_KEY_ID");
        variableValues.add(accessKey);
        variableKeys.add("AWS_SECRET_ACCESS_KEY");
        variableValues.add(accessSecret);

        // Convert Lists to Arrays
        String[] variableKeysArray = variableKeys.toArray(new String[0]);
        String[] variableValuesArray = variableValues.toArray(new String[0]);

        // Construct the Jenkins URL
        UriComponentsBuilder uriBuilder = UriComponentsBuilder.fromHttpUrl(jenkinsUrl + "/job/" + jobName + "/buildWithParameters");

        // Add the variable parameters to the URL
        for (int i = 0; i < variableKeysArray.length; i++) {
            uriBuilder.queryParam(variableKeysArray[i], variableValuesArray[i]);
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
            log.error("Error occurred while sending request to Jenkins: {}", e.getMessage(), e);
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
