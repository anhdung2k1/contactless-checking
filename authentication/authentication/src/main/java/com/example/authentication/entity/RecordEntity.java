package com.example.authentication.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Data
@NoArgsConstructor
@Table(name = "RECORDS")
public class RecordEntity {
    public RecordEntity(String recordData, String status) {
        this.recordData = recordData;
        this.status = status;
        this.createAt = LocalDateTime.now();
    }

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "REC_ID", nullable = false, unique = true)
    private Long recordID;

    @Column(name = "REC_DATA")
    private String recordData;

    @Column(name = "REC_STATUS")
    private String status;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Column(name = "CREATE_AT")
    private LocalDateTime createAt;
}