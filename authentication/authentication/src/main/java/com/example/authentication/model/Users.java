package com.example.authentication.model;

import java.time.LocalDateTime;
import java.util.Date;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Users {
    private Long user_id;
    private String userName;
    private Date birth_day;
    private String address;
    private String gender;
    private LocalDateTime createAt;
    private LocalDateTime updateAt;
}
