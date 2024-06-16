package com.example.authentication.entity;

import java.io.Serializable;
import java.time.LocalDateTime;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import jakarta.transaction.Transactional;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.*;

@Entity
@Data
@Table(name = "ACCOUNTS")
@Transactional(rollbackOn = Exception.class)
public class AccountEntity implements Serializable{
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ACC_ID", nullable = false, unique = true)
    @TableGenerator(name = "ACCOUNT_GEN",
                    table = "SEQUENCER",
                    pkColumnName = "SEQ_NAME",
                    valueColumnName = "SEQ_COUNT",
                    pkColumnValue = "ACCOUNT_SEQ_NEXT_VAL",
                    allocationSize = 1)
    private Long acc_id;
    @Column(name = "USER_NAME", nullable = false, length = 255)
    @NotBlank(message = "Username must not be blank")
    @Size(min = 3, message = "Username must at least 3 characters")
    private String userName;

    @Column(name = "HASH_PASS", nullable = false, length = 64)
    @NotBlank(message = "Password must not be blank")
    @Size(min = 6, message = "Password must be at least 6 characters")
    @JsonIgnore
    private String password;

    @Column(name = "PHONE_NUM")
    private Long phone_number;

    @OneToOne
    @JoinColumn(name = "USER_ID")
    private UserEntity users;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Column(name = "CREATE_AT")
    private LocalDateTime createAt;
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Column(name = "UPDATE_AT")
    private LocalDateTime updateAt;
}
