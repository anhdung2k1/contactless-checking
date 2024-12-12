package com.example.authentication.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import com.example.authentication.entity.TaskEntity;
import com.example.authentication.model.Task;

@Repository
public interface TaskRepository extends JpaRepository<TaskEntity, Long> {
    @Query(value = "SELECT t.* FROM task t " +
            "WHERE t.task_name LIKE %:taskName% ", nativeQuery = true)
    Optional<List<TaskEntity>> findAllTasksByTaskName(String taskName);

    @Query(value = "SELECT COUNT(1) FROM task", nativeQuery = true)
    Long countTasks();

    List<TaskEntity> findByCustomer_CustomerName(String customerName);
}
