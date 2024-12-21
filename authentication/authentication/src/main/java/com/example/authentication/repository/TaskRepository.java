package com.example.authentication.repository;

import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import com.example.authentication.entity.TaskEntity;

@Repository
public interface TaskRepository extends JpaRepository<TaskEntity, Long> {

    @Query("SELECT t FROM TaskEntity t WHERE t.taskName LIKE %:taskName%")
    Page<TaskEntity> findAllTasksByTaskName(String taskName, Pageable pageable);

    @Query("SELECT t FROM TaskEntity t JOIN t.customer c WHERE c.customerName LIKE %:customerName%")
    Page<TaskEntity> findAllTasksByCustomerName(String customerName, Pageable pageable);

    @Query(value = "SELECT COUNT(*) FROM task", nativeQuery = true)
    Long countTasks();

    List<TaskEntity> findByCustomer_CustomerName(String customerName);
}
