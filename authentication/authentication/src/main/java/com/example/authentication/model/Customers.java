package com.example.authentication.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Customers {
    private Long customerID;
    private String customerName;
    private String customerEmail;
    private String customerAddress;
    private String customerGender;
    private String customerBirthDay;
    private String checkInTime;
    private String checkOutTime;
    private LocalDateTime createAt;
    private LocalDateTime updateAt;
    private String photoUrl;
}