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

    @Query(value = "SELECT t.* FROM task t " +
                   "WHERE t.task_name LIKE CONCAT('%', :taskName, '%')", nativeQuery = true)
    Page<TaskEntity> findAllTasksByTaskName(String taskName, Pageable pageable);

    @Query(value = "SELECT t.* " +
                   "FROM task t INNER JOIN customers cus ON cus.cus_id = t.customer_cus_id " +
                   "WHERE cus.cus_name LIKE CONCAT('%', :customerName, '%')", nativeQuery = true)
    Page<TaskEntity> findAllTasksByCustomerName(String customerName, Pageable pageable);

    @Query(value = "SELECT COUNT(*) FROM task", nativeQuery = true)
    Long countTasks();

    List<TaskEntity> findByCustomer_CustomerName(String customerName);
}
