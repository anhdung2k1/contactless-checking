package com.example.authentication.service.implement;

import com.example.authentication.aspect.Utils;
import com.example.authentication.entity.CustomerEntity;
import com.example.authentication.model.Customers;
import com.example.authentication.repository.CustomerRepository;
import com.example.authentication.service.interfaces.CustomerService;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;

@Service
@Transactional(rollbackOn = Exception.class)
@RequiredArgsConstructor
public class CustomerServiceImpl implements CustomerService {
    private final CustomerRepository customerRepository;

    private Map<String, Object> customerMap(CustomerEntity customerEntity) {
        return new HashMap<>() {{
            put("customerID", customerEntity.getCustomerID());
            put("customerName", customerEntity.getCustomerName());
            put("customerGender", customerEntity.getCustomerGender());
            put("customerAddress", customerEntity.getCustomerAddress());
            put("customerBirthDay", Utils.dateToString(customerEntity.getCustomerBirthDay()));
            put("customerEmail", customerEntity.getCustomerEmail());
        }};
    }
    @Override
    public Boolean createCustomer(Customers customers) throws Exception {
        try {
            CustomerEntity customerEntity = new CustomerEntity();
            BeanUtils.copyProperties(customers, customerEntity);
            customerRepository.save(customerEntity);
            return true;
        } catch (Exception e) {
            throw new Exception("Could not create new Customer" + e.getMessage());
        }
    }

    @Override
    public List<Map<String, Object>> getAllCustomersWithName(String customerName) throws Exception {
        try {
            List<Map<String, Object>> customersMapList = new ArrayList<>();
            List<CustomerEntity> customerEntities = customerRepository.findAllCustomersByCustomerName(customerName).isPresent()
                    ? customerRepository.findAllCustomersByCustomerName(customerName).get() : null;
            assert customerEntities != null;
            customerEntities.forEach((customerEntity
                    -> customersMapList.add(customerMap(customerEntity))));
            return customersMapList;
        } catch (NoSuchElementException e) {
            throw new Exception("Could not retrieve all customers with customer Name: " + customerName + e.getMessage());
        }
    }

    @Override
    public Map<String, Object> getCustomerByCustomerId(Long customerId) throws Exception {
        try {
            CustomerEntity customerEntity = customerRepository.findById(customerId).isPresent()
                    ? customerRepository.findById(customerId).get() : null;
            assert customerEntity != null;
            return customerMap(customerEntity);
        } catch (NoSuchElementException e) {
            throw new Exception("Could not get Customer with customer ID: " + customerId + e.getMessage());
        }
    }

    @Override
    public Customers updateCustomerInformation(Long customerId, Customers customers) throws Exception {
        try {
            CustomerEntity customerEntity = customerRepository.findById(customerId).isPresent()
                    ? customerRepository.findById(customerId).get() : null;
            assert customerEntity != null;
            customerEntity.setCustomerName(customers.getCustomerName());
            customerEntity.setCustomerGender(customers.getCustomerGender());
            customerEntity.setCustomerAddress(customers.getCustomerAddress());
            customerEntity.setCustomerBirthDay(Utils.stringToDate(customers.getCustomerBirthDay()));
            customerEntity.setCustomerEmail(customers.getCustomerEmail());
            customerEntity.setUpdateAt(LocalDateTime.now());
            customerRepository.save(customerEntity);

            return customers;
        } catch (NoSuchElementException e) {
            throw new Exception("Could not get Customer with customer ID: " + customerId + e.getMessage());
        }
    }

    @Override
    public Boolean deleteCustomer(Long customerId) throws Exception {
        try {
            if(customerRepository.findById(customerId).isPresent()) {
                customerRepository.delete(customerRepository.findById(customerId).get());
                return true;
            }
            return false;
        } catch (NoSuchElementException e) {
            throw new Exception("Could not found customer with customerId: " + customerId + e.getMessage());
        }
    }
}