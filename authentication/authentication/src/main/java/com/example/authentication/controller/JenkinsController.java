package com.example.authentication.controller;

import com.example.authentication.service.interfaces.JenkinsService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/jenkins")
@RequiredArgsConstructor
public class JenkinsController {

    private final JenkinsService jenkinsService;

    @PostMapping("/buildWithParameters")
    @ResponseBody
    public ResponseEntity<String> triggerJenkinsJob(@RequestBody Map<String, Object> params) {
        return ResponseEntity.ok(jenkinsService.requestBuildWithParameters(params));
    }
}
