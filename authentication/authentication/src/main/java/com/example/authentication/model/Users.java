package com.example.authentication.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Users {
    private Long user_id;
    private String userName;
    private String birthDay;
    private String address;
    private String gender;
    private String imageUrl;
    private LocalDateTime createAt;
    private LocalDateTime updateAt;
}