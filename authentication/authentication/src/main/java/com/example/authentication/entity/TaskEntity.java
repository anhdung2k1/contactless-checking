package com.example.authentication.entity;

import java.time.LocalDateTime;

import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonFormat;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
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
        this.createAt = LocalDateTime.now();
        this.updateAt = LocalDateTime.now();
    }

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "TASK_ID", nullable = false, unique = true)
    @TableGenerator(name = "TASK_CUS_GEN", table = "SEQUENCER", pkColumnName = "SEQ_NAME", valueColumnName = "SEQ_COUNT", pkColumnValue = "TASK_CUS_SEQ_NEXT_VAL", allocationSize = 1)
    private Long taskId;

    @Column(name = "TASK_STATUS")
    private String taskStatus;

    @Column(name = "TASK_DESC")
    private String taskDesc;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Column(name = "CREATE_AT")
    private LocalDateTime createAt;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Column(name = "UPDATE_AT")
    private LocalDateTime updateAt;

}
