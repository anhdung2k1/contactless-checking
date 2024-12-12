package com.example.authentication.service.implement;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.stream.Collectors;

import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;

import com.example.authentication.entity.CustomerEntity;
import com.example.authentication.entity.NotificationEntity;
import com.example.authentication.entity.TaskEntity;
import com.example.authentication.model.Task;
import com.example.authentication.repository.CustomerRepository;
import com.example.authentication.repository.NotificationRepository;
import com.example.authentication.repository.TaskRepository;
import com.example.authentication.service.interfaces.TaskService;

import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@Transactional(rollbackOn = Exception.class)
@RequiredArgsConstructor
@Slf4j
public class TaskServiceImpl implements TaskService {
    private final TaskRepository taskRepository;
    private final NotificationRepository notificationRepository;
    private final CustomerRepository customerRepository;

    private Map<String, Object> taskMap(TaskEntity taskEntity) {
        return new HashMap<>() {
            {
                put("taskId", taskEntity.getTaskId());
                put("taskStatus", taskEntity.getTaskStatus());
                put("taskDesc", taskEntity.getTaskDesc());
                put("taskName", taskEntity.getTaskName());
                put("customerName", taskEntity.getCustomer() != null ? taskEntity.getCustomer().getCustomerName() : "");
            }
        };
    }

    @Override
    public Boolean createTask(Task tasks) throws Exception {
        try {
            TaskEntity taskEntity = new TaskEntity();
            BeanUtils.copyProperties(tasks, taskEntity);
            log.info("Create Task: {}", taskEntity);
            taskRepository.save(taskEntity);

            // Create Notification
            String notificationMessage = String.format("New Task %s created successfully",
                    tasks.getTaskStatus());
            NotificationEntity notificationEntity = new NotificationEntity(notificationMessage);
            notificationRepository.save(notificationEntity);
            log.info("Save notification: {}", notificationEntity);
            return true;
        } catch (Exception e) {
            throw new Exception("Could not create new Task" + e.getMessage());
        }
    }

    @Override
    public Long countTasks() throws Exception {
        try {
            log.info("Count Tasks: {}", taskRepository.countTasks());
            return taskRepository.countTasks();
        } catch (NoSuchElementException e) {
            throw new Exception("Could not count task: " + e.getMessage());
        }
    }

    @Override
    public List<Map<String, Object>> getAllTasksWithTaskName(String taskName) throws Exception {
        try {
            List<Map<String, Object>> tasksMapList = new ArrayList<>();
            List<TaskEntity> taskEntities = taskRepository.findAllTasksByTaskName(taskName)
                    .isPresent()
                            ? taskRepository.findAllTasksByTaskName(taskName).get()
                            : null;
            assert taskEntities != null;
            taskEntities.forEach((taskEntity -> {
                log.info("taskEntity: {}", taskEntity);
                tasksMapList.add(taskMap(taskEntity));
            }));
            return tasksMapList;
        } catch (NoSuchElementException e) {
            throw new Exception(
                    "Could not retrieve all task with task Name: " + taskName + e.getMessage());
        }
    }

    @Override
    public Map<String, Object> getTaskByTaskId(Long taskId) throws Exception {
        try {
            TaskEntity taskEntity = taskRepository.findById(taskId).isPresent()
                    ? taskRepository.findById(taskId).get()
                    : null;
            assert taskEntity != null;
            log.info("taskEntity: {}", taskEntity);
            return taskMap(taskEntity);
        } catch (NoSuchElementException e) {
            throw new Exception("Could not get Task with task ID: " + taskId + e.getMessage());
        }
    }

    @Override
    public Task updateTaskDescription(Long taskId, Task tasks) throws Exception {
        try {
            TaskEntity taskEntity = taskRepository.findById(taskId).isPresent()
                    ? taskRepository.findById(taskId).get()
                    : null;
            assert taskEntity != null;

            if (tasks.getTaskName() != null) {
                taskEntity.setTaskName(tasks.getTaskName());
            }
            if (tasks.getTaskStatus() != null) {
                taskEntity.setTaskStatus(tasks.getTaskStatus());
            }
            if (tasks.getTaskDesc() != null) {
                taskEntity.setTaskDesc(tasks.getTaskDesc());
            }
            if (tasks.getCustomer().getCustomerName() != null || !tasks.getCustomer().getCustomerName().isEmpty()) {
                if (customerRepository.findCustomerByCustomerName(tasks.getCustomer().getCustomerName()).isPresent()) {
                    CustomerEntity customerEntity = customerRepository
                            .findCustomerByCustomerName(tasks.getCustomer().getCustomerName()).get();
                    log.info("updateTaskDescription:(), customerEntity: {}", customerEntity);
                    taskEntity.setCustomer(customerEntity);
                }
            }
            taskEntity.setUpdateAt(LocalDateTime.now());
            log.info("updateTaskDescription:(), taskEntity: {}", taskEntity);

            taskRepository.save(taskEntity);
            BeanUtils.copyProperties(taskEntity, tasks);

            // Create Notification
            String notificationMessage = String.format("Task %s updated successfully", tasks.getTaskStatus());
            NotificationEntity notificationEntity = new NotificationEntity(notificationMessage);
            notificationRepository.save(notificationEntity);
            return tasks;
        } catch (

        NoSuchElementException e) {
            throw new Exception("Could not get Task with task ID: " + taskId + ". " + e.getMessage());
        }
    }

    @Override
    public Boolean deleteTask(Long taskId) throws Exception {
        try {
            if (taskRepository.findById(taskId).isPresent()) {
                log.info("taskFindById: {}", taskRepository.findById(taskId).get());
                taskRepository.delete(taskRepository.findById(taskId).get());
                return true;
            }
            return false;
        } catch (NoSuchElementException e) {
            throw new Exception("Could not found task with task: " + taskId + e.getMessage());
        }
    }

    @Override
    public List<Task> getAllTasks() {
        List<TaskEntity> taskEntities = taskRepository.findAll();
        log.info("GetAllTasks: {}", taskEntities);
        return taskEntities.stream()
                .map(task -> new Task(
                        task.getTaskId(),
                        task.getTaskStatus(),
                        task.getTaskDesc(),
                        task.getTaskName(),
                        task.getCustomer(),
                        task.getCreateAt(),
                        task.getUpdateAt()))
                .collect(Collectors.toList());
    }

    public List<TaskEntity> getTasksByCustomerName(String customerName) {
        log.info("getTaskByCustomerName: {}", taskRepository.findByCustomer_CustomerName(customerName));
        return taskRepository.findByCustomer_CustomerName(customerName);
    }
}
