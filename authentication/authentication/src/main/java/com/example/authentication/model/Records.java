package com.example.authentication.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Records {
    private Long recordID;
    private String recordData;
    private String status;
    private LocalDateTime createAt;
}
