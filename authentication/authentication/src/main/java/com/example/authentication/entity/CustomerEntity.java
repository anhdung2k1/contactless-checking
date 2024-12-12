package com.example.authentication.entity;

import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonManagedReference;
import jakarta.persistence.*;
import jakarta.transaction.Transactional;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.*;

@Entity
@Data
@Table(name = "CUSTOMERS")
@Transactional(rollbackOn = Exception.class)
public class CustomerEntity {
    public CustomerEntity() {
        this.customerName = "";
        this.customerAddress = "";
        this.customerGender = "";
        this.customerBirthDay = new Date();
        this.customerEmail = "";
        this.checkInTime = new Date();
        this.checkOutTime = new Date();
        this.planWeight = 0;
        this.currWeight = 0;
        this.planBodyType = "";
        this.currBodyType = "";
        this.createAt = LocalDateTime.now();
        this.updateAt = LocalDateTime.now();
    }

    public CustomerEntity(String customerName) {
        this.customerName = customerName;
        this.customerAddress = "";
        this.customerGender = "";
        this.customerBirthDay = new Date();
        this.customerEmail = "";
        this.planWeight = 0;
        this.currWeight = 0;
        this.planBodyType = "";
        this.currBodyType = "";
        this.createAt = LocalDateTime.now();
        this.updateAt = LocalDateTime.now();
    }

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "CUS_ID", nullable = false, unique = true)
    @TableGenerator(name = "CUS_GEN", table = "SEQUENCER", pkColumnName = "SEQ_NAME", valueColumnName = "SEQ_COUNT", pkColumnValue = "CUS_SEQ_NEXT_VAL", allocationSize = 1)
    private Long customerID;

    @Column(name = "CUS_NAME", nullable = false)
    @NotBlank(message = "Customer Name must not be blank")
    @Size(min = 3, message = "Customer Name at least 3 characters")
    private String customerName;

    @Column(name = "CUS_ADDRESS")
    private String customerAddress;

    @Column(name = "CUS_GENDER")
    private String customerGender;

    @Column(name = "CUS_BIRTH_DAY")
    @JsonFormat(pattern = "yyyy-MM-dd")
    private Date customerBirthDay;

    @Column(name = "CUS_EMAIL")
    private String customerEmail;

    @OneToMany(mappedBy = "customer", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @JsonManagedReference
    private Set<PhotoEntity> photos = new HashSet<>();

    @OneToMany(mappedBy = "customer")
    private Set<TaskEntity> tasks = new HashSet<>();

    @Column(name = "CHECK_IN_TIME")
    @JsonFormat(pattern = "yyyy-MM-dd")
    private Date checkInTime;

    @Column(name = "CHECK_OUT_TIME")
    @JsonFormat(pattern = "yyyy-MM-dd")
    private Date checkOutTime;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Column(name = "CREATE_AT")
    private LocalDateTime createAt;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Column(name = "UPDATE_AT")
    private LocalDateTime updateAt;

    @Column(name = "CUS_PLAN_WEIGHT")
    private int planWeight;

    @Column(name = "CUS_CURR_WEIGHT")
    private int currWeight;

    @Column(name = "CUS_PLAN_BODYTYPE")
    private String planBodyType;

    @Column(name = "CUS_CURR_BODYTYPE")
    private String currBodyType;
}