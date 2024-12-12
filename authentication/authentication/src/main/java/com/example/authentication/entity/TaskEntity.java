package com.example.authentication.entity;

import java.time.LocalDateTime;

import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonFormat;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import jakarta.persistence.TableGenerator;
import jakarta.transaction.Transactional;
import lombok.Data;

@Entity
@Data
@Table(name = "TASK")
@Transactional(rollbackOn = Exception.class)
public class TaskEntity {
    public TaskEntity() {
        this.taskStatus = "";
        this.taskDesc = "";
        this.taskName = "";
        this.createAt = LocalDateTime.now();
        this.updateAt = LocalDateTime.now();
    }

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "TASK_ID", nullable = false, unique = true)
    @TableGenerator(name = "TASK_CUS_GEN", table = "SEQUENCER", pkColumnName = "SEQ_NAME", valueColumnName = "SEQ_COUNT", pkColumnValue = "TASK_CUS_SEQ_NEXT_VAL", allocationSize = 1)
    private Long taskId;

    @ManyToOne
    private CustomerEntity customer;

    @Column(name = "TASK_STATUS") // Lưu giá trị enum dưới dạng chuỗi
    private String taskStatus;

    @Column(name = "TASK_DESC")
    private String taskDesc;

    @Column(name = "TASK_NAME")
    private String taskName;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Column(name = "CREATE_AT")
    private LocalDateTime createAt;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Column(name = "UPDATE_AT")
    private LocalDateTime updateAt;

}
