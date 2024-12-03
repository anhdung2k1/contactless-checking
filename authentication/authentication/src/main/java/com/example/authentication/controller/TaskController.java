package com.example.authentication.controller;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.example.authentication.model.Task;
import com.example.authentication.service.interfaces.TaskService;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class TaskController {
    private final TaskService taskService;

    @PostMapping(value = "/tasks")
    public ResponseEntity<Boolean> createTask(@RequestBody Task tasks) throws Exception {
        return ResponseEntity.ok(taskService.createTask(tasks));
    }

    @GetMapping(value = "/tasks")
    public ResponseEntity<List<Task>> getAllTasks() {
        return ResponseEntity.ok(taskService.getAllTasks());
    }

    // Get all customers with customer Name
    @GetMapping(value = "/tasks/query")
    public ResponseEntity<List<Map<String, Object>>> getAllTasksWithStatus(@RequestParam("query") String taskStatus)
            throws Exception {
        return ResponseEntity.ok(taskService.getAllTasksWithStatus(taskStatus));
    }

    // Get Customer by customer ID
    @GetMapping(value = "/tasks/{taskId}")
    public ResponseEntity<Map<String, Object>> getTaskByTaskId(@PathVariable("taskId") Long taskId)
            throws Exception {
        return ResponseEntity.ok(taskService.getTaskByTaskId(taskId));
    }

    // Count Customer
    @GetMapping(value = "/tasks/count")
    public ResponseEntity<Long> getAllRecords() throws Exception {
        return ResponseEntity.ok(taskService.countTasks());
    }

    // Update Customer Information
    @PatchMapping(value = "/tasks/{taskId}")
    public ResponseEntity<Task> updateTaskDescription(@PathVariable("taskId") Long taskId,
            @RequestBody Task task) throws Exception {
        return ResponseEntity.ok(taskService.updateTaskDescription(taskId, task));
    }

    // Delete Customer
    @DeleteMapping(value = "/tasks/{taskId}")
    public ResponseEntity<Map<String, Boolean>> deleteTask(@PathVariable("taskId") Long taskId)
            throws Exception {
        return ResponseEntity.ok(new HashMap<>() {
            {
                put("deleted", taskService.deleteTask(taskId));
            }
        });
    }
}
