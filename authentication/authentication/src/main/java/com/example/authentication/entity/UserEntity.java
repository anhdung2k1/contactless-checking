package com.example.authentication.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import jakarta.persistence.*;
import jakarta.transaction.Transactional;
import lombok.Getter;
import lombok.Setter;

import java.io.Serializable;
import java.time.LocalDateTime;

@Getter
@Setter
@Entity
@Table(name = "USERS")
@Transactional(rollbackOn = Exception.class)
public class UserEntity implements Serializable{
    //Default Constructor
    public UserEntity(){
        this.address = "UNKNOWN";
        this.gender = "";
        this.birthDay = "2000-01-01";
        this.userName = "UNKNOWN";
        this.imageUrl = "";
        this.createAt = LocalDateTime.now();
        this.updateAt = LocalDateTime.now();
    }
    public UserEntity(String userName) {
        this.userName = userName;
        this.address = "UNKNOWN";
        this.gender = "";
        this.imageUrl = "";
        this.birthDay = "2000-01-01";
        this.createAt = LocalDateTime.now();
        this.updateAt = LocalDateTime.now();
    }

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "USER_ID", nullable = false, unique = true)
    @TableGenerator(name = "USER_GEN",
            table = "SEQUENCER",
            pkColumnName = "SEQ_NAME",
            valueColumnName = "SEQ_COUNT",
            pkColumnValue = "USER_SEQ_NEXT_VAL",
            allocationSize = 1)
    private Long user_id;

    @Column(name = "USER_NAME", nullable = false, length = 20)
    private String userName;

    @Column(name = "BIRTH_DAY")
    private String birthDay;

    @Column(name = "ADDRESS", length = 30)
    private String address;

    @Column(name = "GENDER", length = 10)
    private String gender;

    @Column(name = "IMAGE_URL")
    private String imageUrl;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Column(name = "CREATE_AT")
    private LocalDateTime createAt;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Column(name = "UPDATE_At")
    private LocalDateTime updateAt;
}