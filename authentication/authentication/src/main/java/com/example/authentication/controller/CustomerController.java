package com.example.authentication.controller;

import com.example.authentication.model.Customers;
import com.example.authentication.service.interfaces.CustomerService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class CustomerController {
    private final CustomerService customerService;
    // Create new Customer
    @PostMapping(value = "/customers")
    public ResponseEntity<Boolean> createCustomer(@RequestBody Customers customers) throws Exception {
        return ResponseEntity.ok(customerService.createCustomer(customers));
    }
    // Get all customers with customer Name
    @GetMapping(value = "/customers/query")
    public ResponseEntity<List<Map<String, Object>>> getAllCustomersWithName(@RequestParam("query") String customerName) throws Exception {
        return ResponseEntity.ok(customerService.getAllCustomersWithName(customerName));
    }
    // Get Customer by customer ID
    @GetMapping(value = "/customers/{customerId}")
    public ResponseEntity<Map<String, Object>> getCustomerByCustomerId(@PathVariable("customerId") Long customerId) throws Exception {
        return ResponseEntity.ok(customerService.getCustomerByCustomerId(customerId));
    }
    // Count Customer
    @GetMapping(value = "/customers/count")
    public ResponseEntity<Long> getAllRecords() throws Exception {
        return ResponseEntity.ok(customerService.countCustomers());
    }

    // Get Customer Check In Time
    @GetMapping(value = "/customers/getCheckIn/{customerId}")
    public ResponseEntity<Map<String, Object>> getCheckIn(@PathVariable("customerId") Long customerId) throws Exception {
        return ResponseEntity.ok(new HashMap<>() {{
            put("customerName", customerService.getCustomerByCustomerId(customerId).get("customerName"));
            put("checkInTime", customerService.getCustomerCheckInTime(customerId));
        }});
    }

    // Get Customer Check Out Time
    @GetMapping(value = "/customers/getCheckOut/{customerId}")
    public ResponseEntity<Map<String, Object>> getCheckOut(@PathVariable("customerId") Long customerId) throws Exception {
        return ResponseEntity.ok(new HashMap<>() {{
            put("customerName", customerService.getCustomerByCustomerId(customerId).get("customerName"));
            put("checkOutTime", customerService.getCustomerCheckOutTime(customerId));
        }});
    }

    // Update Customer Information
    @PatchMapping(value = "/customers/{customerId}")
    public ResponseEntity<Customers> updateCustomerInformation(@PathVariable("customerId") Long customerId, @RequestBody Customers customers) throws Exception {
        return ResponseEntity.ok(customerService.updateCustomerInformation(customerId, customers));
    }
    // Delete Customer
    @DeleteMapping(value = "/customers/{customerId}")
    public ResponseEntity<Map<String, Boolean>> deleteCustomer(@PathVariable("customerId") Long customerId) throws Exception {
        return ResponseEntity.ok(new HashMap<>() {{
            put("deleted", customerService.deleteCustomer(customerId));
        }});
    }
}