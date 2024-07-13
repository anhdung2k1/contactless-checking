package com.example.authentication.entity;

import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonFormat;
import jakarta.persistence.*;
import jakarta.transaction.Transactional;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Data
@NoArgsConstructor
@Table(name = "PHOTOS")
@Transactional(rollbackOn = Exception.class)
public class PhotoEntity {
    public PhotoEntity(String photoUrl) {
        this.photoUrl = photoUrl;
        this.uploadAt = LocalDateTime.now();
    }
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "PHOTO_ID", nullable = false, unique = true)
    @TableGenerator(name = "PHOTO_GEN",
            table = "SEQUENCER",
            pkColumnName = "SEQ_NAME",
            valueColumnName = "SEQ_COUNT",
            pkColumnValue = "PHOTO_SEQ_NEXT_VAL",
            allocationSize = 1)
    private Long photoID;

    @Column(name = "PHOTO_URL", nullable = false)
    private String photoUrl;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Column(name = "UPLOAD_AT")
    private LocalDateTime uploadAt;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "CUS_ID", nullable = false)
    @JsonBackReference
    private CustomerEntity customer;
}
