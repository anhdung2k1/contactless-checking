package com.example.authentication.service.interfaces;

import com.example.authentication.model.Customers;
import java.util.List;
import java.util.Map;

import org.springframework.data.domain.Page;

public interface CustomerService {
    Boolean createCustomer(Customers customers) throws Exception;

    Long countCustomers() throws Exception;

    // List<Map<String, Object>> getAllCustomersWithName(String customerName) throws
    // Exception;
    public Page<Map<String, Object>> getAllCustomersWithName(String customerName, int page, int size) throws Exception;

    Map<String, Object> getCustomerByCustomerId(Long customerId) throws Exception;

    List<String> getCustomerCheckInTime(Long customerId) throws Exception;

    List<String> getCustomerCheckOutTime(Long customerId) throws Exception;

    Customers updateCustomerInformation(Long customerId, Customers customers) throws Exception;

    Boolean deleteCustomer(Long customerId) throws Exception;

    // List<Customers> getAllCustomers();
    public Page<Customers> getAllCustomers(int page, int size);

}