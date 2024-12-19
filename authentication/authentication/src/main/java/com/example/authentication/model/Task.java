package com.example.authentication.model;

import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Task {
    private Long taskId;
    private String taskStatus;
    private String taskDesc;
    private String taskName;
    private String customerName;
    private Long estimateHours;
    private Long logHours;
    private LocalDateTime createAt;
    private LocalDateTime updateAt;
}
