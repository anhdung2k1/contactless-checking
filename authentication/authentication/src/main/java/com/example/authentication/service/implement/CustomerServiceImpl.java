package com.example.authentication.service.implement;

import com.amazonaws.services.s3.AmazonS3;
import com.example.authentication.Utils.S3Utils;
import com.example.authentication.aspect.Utils;
import com.example.authentication.entity.CustomerEntity;
import com.example.authentication.entity.NotificationEntity;
import com.example.authentication.entity.PhotoEntity;
import com.example.authentication.model.Customers;
import com.example.authentication.repository.CustomerRepository;
import com.example.authentication.repository.NotificationRepository;
import com.example.authentication.repository.PhotoRepository;
import com.example.authentication.service.interfaces.CustomerService;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;

import java.net.URL;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@Transactional(rollbackOn = Exception.class)
@RequiredArgsConstructor
@Slf4j
public class CustomerServiceImpl implements CustomerService {
    private final S3Utils s3Utils;

    @Value("${bucket.name}")
    public String bucketName;
    @Autowired
    public AmazonS3 s3Client;

    private final CustomerRepository customerRepository;
    private final PhotoRepository photoRepository;
    private final NotificationRepository notificationRepository;
    private static String filePath = "arcface_train_dataset/%s/";

    private Map<String, Object> customerMap(CustomerEntity customerEntity) {
        return new HashMap<>() {
            {
                put("customerID", customerEntity.getCustomerID());
                put("customerName", customerEntity.getCustomerName());
                put("customerGender", customerEntity.getCustomerGender());
                put("customerAddress", customerEntity.getCustomerAddress());
                put("customerBirthDay", Utils.dateToString(customerEntity.getCustomerBirthDay()));
                put("customerEmail", customerEntity.getCustomerEmail());
                put("checkInTime", customerEntity.getCheckInTime());
                put("checkOutTime", customerEntity.getCheckOutTime());
            }
        };
    }

    @Override
    public Boolean createCustomer(Customers customers) throws Exception {
        try {
            CustomerEntity customerEntity = new CustomerEntity();
            BeanUtils.copyProperties(customers, customerEntity);
            log.info("Set customerBirthDat: {}", Utils.stringToDate(customers.getCustomerBirthDay()));
            customerEntity.setCustomerBirthDay(Utils.stringToDate(customers.getCustomerBirthDay()));
            customerRepository.save(customerEntity);
            log.info("Save customer: {}", customerEntity);
            // Create Notification
            String notificationMessage = String.format("New Customer %s created successfully",
                    customers.getCustomerName());
            log.info("Notification message: {}", notificationMessage);
            NotificationEntity notificationEntity = new NotificationEntity(notificationMessage);
            notificationRepository.save(notificationEntity);
            log.info("Save notification: {}", notificationEntity);
            return true;
        } catch (Exception e) {
            throw new Exception("Could not create new Customer" + e.getMessage());
        }
    }

    @Override
    public Page<Map<String, Object>> getAllCustomersWithName(String customerName, int page, int size) throws Exception {
        try {
            Pageable pageable = PageRequest.of(page, size);
            Page<CustomerEntity> customerPage = customerRepository.findAllCustomersByCustomerName(customerName,
                    pageable);

            // Map từng CustomerEntity sang Map<String, Object>
            return customerPage.map(this::customerMap);
        } catch (Exception e) {
            throw new Exception(
                    "Could not retrieve all customers with customer name: " + customerName + e.getMessage());
        }
    }

    @Override
    public Map<String, Object> getCustomerByCustomerId(Long customerId) throws Exception {
        try {
            CustomerEntity customerEntity = customerRepository.findById(customerId).isPresent()
                    ? customerRepository.findById(customerId).get()
                    : null;
            assert customerEntity != null;
            return customerMap(customerEntity);
        } catch (NoSuchElementException e) {
            throw new Exception("Could not get Customer with customer ID: " + customerId + e.getMessage());
        }
    }

    @Override
    public Long countCustomers() throws Exception {
        try {
            return customerRepository.countCustomers();
        } catch (NoSuchElementException e) {
            throw new Exception("Could not count customer: " + e.getMessage());
        }
    }

    @Override
    public List<String> getCustomerCheckInTime(Long customerId) throws Exception {
        try {
            List<Date> checkInTime = customerRepository.retrieveCustomerCheckInTimeWithId(customerId).isPresent()
                    ? customerRepository.retrieveCustomerCheckInTimeWithId(customerId).get()
                    : null;
            assert checkInTime != null;
            log.info("Check In Time: {}", checkInTime);
            List<String> checkInTimeStr = checkInTime.stream().map(
                    Utils::dateToString).collect(Collectors.toList());
            log.info("Check In Time Str: {}", checkInTimeStr);
            return checkInTimeStr;
        } catch (Exception e) {
            throw new Exception("Could not get the customer check in time !! Seems error during fetch data");
        }
    }

    @Override
    public List<String> getCustomerCheckOutTime(Long customerId) throws Exception {
        try {
            List<Date> checkOutTime = customerRepository.retrieveCustomerCheckOutTimeWithId(customerId).isPresent()
                    ? customerRepository.retrieveCustomerCheckOutTimeWithId(customerId).get()
                    : null;
            assert checkOutTime != null;
            log.info("Check Out Time: {}", checkOutTime);
            List<String> checkOutTimeStr = checkOutTime.stream().map(
                    Utils::dateToString).collect(Collectors.toList());
            log.info("Check Out Time Str: {}", checkOutTimeStr);
            return checkOutTimeStr;
        } catch (Exception e) {
            throw new Exception("Could not get the customer check in time !! Seems error during fetch data");
        }
    }

    @Override
    public Customers updateCustomerInformation(Long customerId, Customers customers) throws Exception {
        try {
            CustomerEntity customerEntity = customerRepository.findById(customerId).isPresent()
                    ? customerRepository.findById(customerId).get()
                    : null;
            assert customerEntity != null;

            if (customers.getCustomerName() != null) {
                customerEntity.setCustomerName(customers.getCustomerName());
            }
            if (customers.getCustomerGender() != null) {
                customerEntity.setCustomerGender(customers.getCustomerGender());
            }
            if (customers.getCustomerAddress() != null) {
                customerEntity.setCustomerAddress(customers.getCustomerAddress());
            }
            if (customers.getCustomerBirthDay() != null) {
                customerEntity.setCustomerBirthDay(Utils.stringToDate(customers.getCustomerBirthDay()));
            }
            if (customers.getCustomerEmail() != null) {
                customerEntity.setCustomerEmail(customers.getCustomerEmail());
            }

            customerEntity.setUpdateAt(LocalDateTime.now());
            if (customers.getPhotoUrl() != null) {
                String photo = customers.getPhotoUrl();
                filePath = String.format(filePath, customerEntity.getCustomerName());
                URL objectURL = s3Utils.getS3URL(filePath, photo);
                PhotoEntity photoEntity = new PhotoEntity(objectURL.toString());
                photoEntity.setCustomer(customerEntity);
                photoRepository.save(photoEntity);
            }
            customerRepository.save(customerEntity);
            BeanUtils.copyProperties(customerEntity, customers);

            // Create Notification
            String notificationMessage = String.format("Customer %s updated successfully", customers.getCustomerName());
            NotificationEntity notificationEntity = new NotificationEntity(notificationMessage);
            notificationRepository.save(notificationEntity);
            return customers;
        } catch (NoSuchElementException e) {
            throw new Exception("Could not get Customer with customer ID: " + customerId + ". " + e.getMessage());
        }
    }

    @Override
    public Boolean deleteCustomer(Long customerId) throws Exception {
        try {
            if (customerRepository.findById(customerId).isPresent()) {
                customerRepository.delete(customerRepository.findById(customerId).get());
                return true;
            }
            return false;
        } catch (NoSuchElementException e) {
            throw new Exception("Could not found customer with customerId: " + customerId + e.getMessage());
        }
    }

    @Override
    public Page<Customers> getAllCustomers(int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<CustomerEntity> customerEntities = customerRepository.findAll(pageable);

        // Chuyển đổi từ CustomerEntity sang Customers
        return customerEntities.map(entity -> new Customers(
                entity.getCustomerID(),
                entity.getCustomerName(),
                entity.getCustomerEmail(),
                entity.getCustomerAddress(),
                entity.getCustomerGender(),
                new SimpleDateFormat("yyyy-MM-dd").format(entity.getCustomerBirthDay()),
                new SimpleDateFormat("yyyy-MM-dd").format(entity.getCheckInTime()),
                new SimpleDateFormat("yyyy-MM-dd").format(entity.getCheckOutTime()),
                entity.getCreateAt(),
                entity.getUpdateAt(),
                entity.getPhotos() != null && !entity.getPhotos().isEmpty()
                        ? entity.getPhotos().iterator().next().getPhotoUrl()
                        : null
                ));
    }
}