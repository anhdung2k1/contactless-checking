package com.example.authentication.service.interfaces;

import java.util.Map;

public interface JenkinsService {
    String requestBuildWithParameters(Map<String, Object> params);
}
