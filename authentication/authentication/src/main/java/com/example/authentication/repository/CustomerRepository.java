package com.example.authentication.repository;

import com.example.authentication.entity.CustomerEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.Optional;

public interface CustomerRepository extends JpaRepository<CustomerEntity, Long> {
    @Query(value = "SELECT cus.* FROM customers cus " +
            "WHERE cus.cus_name LIKE %:customerName% " +
            "LIMIT 28", nativeQuery = true)
    Optional<List<CustomerEntity>> findAllCustomersByCustomerName(String customerName);
}