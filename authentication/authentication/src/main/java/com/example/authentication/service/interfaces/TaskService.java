package com.example.authentication.service.interfaces;

import java.util.List;
import java.util.Map;

import org.springframework.data.domain.Page;

import com.example.authentication.entity.TaskEntity;
import com.example.authentication.model.Task;

public interface TaskService {
    Boolean createTask(Task tasks) throws Exception;

    Long countTasks() throws Exception;

    Page<Map<String, Object>> getAllTasksWithTaskName(String taskName, int page, int size) throws Exception;

    Map<String, Object> getTaskByTaskId(Long taskId) throws Exception;

    Task updateTaskDescription(Long taskId, Task tasks) throws Exception;

    Boolean deleteTask(Long taskId) throws Exception;

    Page<Task> getAllTasks(int page, int size);

    List<TaskEntity> getTasksByCustomerName(String customerName);
}
