package com.example.authentication.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Data
@NoArgsConstructor
@Table(name = "NOTIFICATIONS")
public class NotificationEntity {
    public NotificationEntity(String notificationMessage) {
        this.notificationMessage = notificationMessage;
        this.createAt = LocalDateTime.now();
    }

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "NOTIF_ID", nullable = false, unique = true)
    private Long notificationID;

    @Column(name = "NOTIF_MESSAGE")
    private String notificationMessage;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Column(name = "CREATE_AT")
    private LocalDateTime createAt;
}