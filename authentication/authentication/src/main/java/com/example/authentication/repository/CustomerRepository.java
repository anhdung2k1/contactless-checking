package com.example.authentication.repository;

import com.example.authentication.entity.CustomerEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.Date;
import java.util.List;
import java.util.Optional;

@Repository
public interface CustomerRepository extends JpaRepository<CustomerEntity, Long> {

        // Phân trang theo tên khách hàng
        @Query(value = "SELECT cus.* FROM customers cus " +
                        "WHERE cus.cus_name LIKE %:customerName% ", countQuery = "SELECT COUNT(1) FROM customers cus WHERE cus.cus_name LIKE %:customerName%", nativeQuery = true)
        Page<CustomerEntity> findAllCustomersByCustomerName(String customerName, Pageable pageable);

        // Tìm một khách hàng cụ thể theo tên
        @Query(value = "SELECT cus.* FROM customers cus " +
                        "WHERE cus.cus_name =:customerName", nativeQuery = true)
        Optional<CustomerEntity> findCustomerByCustomerName(String customerName);

        // Đếm tổng số khách hàng
        @Query(value = "SELECT COUNT(1) FROM customers", nativeQuery = true)
        Long countCustomers();

        // Lấy danh sách thời gian check-in theo ID khách hàng
        @Query(value = "SELECT cus.check_in_time FROM customers cus " +
                        "WHERE cus.cus_id =:customerId", nativeQuery = true)
        Optional<List<Date>> retrieveCustomerCheckInTimeWithId(Long customerId);

        // Lấy danh sách thời gian check-out theo ID khách hàng
        @Query(value = "SELECT cus.check_out_time FROM customers cus " +
                        "WHERE cus.cus_id =:customerId", nativeQuery = true)
        Optional<List<Date>> retrieveCustomerCheckOutTimeWithId(Long customerId);
}
