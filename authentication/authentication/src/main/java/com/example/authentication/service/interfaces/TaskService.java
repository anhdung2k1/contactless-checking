package com.example.authentication.service.interfaces;

import java.util.List;
import java.util.Map;

import com.example.authentication.entity.TaskEntity;
import com.example.authentication.model.Task;

public interface TaskService {
    Boolean createTask(Task tasks) throws Exception;

    Long countTasks() throws Exception;

    List<Map<String, Object>> getAllTasksWithStatus(String taskStatus) throws Exception;

    Map<String, Object> getTaskByTaskId(Long taskId) throws Exception;

    Task updateTaskDescription(Long taskId, Task tasks) throws Exception;

    Boolean deleteTask(Long taskId) throws Exception;

    List<Task> getAllTasks();
}
