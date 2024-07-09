package com.example.authentication.model;

import java.time.LocalDateTime;

import com.example.authentication.entity.UserEntity;

import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Accounts {
    public Accounts(String userName, String password) {
        this.userName = userName;
        this.password = password;
    }
    private Long acc_id;
    private String userName;
    private String password;
    private Long phoneNumber;
    private UserEntity users;
    private LocalDateTime createAt;
    private LocalDateTime updateAt;
}
