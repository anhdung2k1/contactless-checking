package com.example.authentication.controller;

import com.example.authentication.entity.NotificationEntity;
import com.example.authentication.entity.RecordEntity;
import com.example.authentication.model.Records;
import com.example.authentication.service.interfaces.NotificationRecordService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class NotificationRecordController {
    private final NotificationRecordService notificationRecordService;

    // Create new Notification
    @PostMapping(value = "/notifications")
    public ResponseEntity<Boolean> createNotification(@RequestBody String message) throws Exception {
        return ResponseEntity.ok(notificationRecordService.createNotification(message));
    }

    // Get all Notifications
    @GetMapping(value = "/notifications")
    public ResponseEntity<List<NotificationEntity>> getAllNotifications() throws Exception {
        return ResponseEntity.ok(notificationRecordService.getAllNotifications());
    }

    // Delete all Notifications
    @DeleteMapping(value = "/notifications")
    public ResponseEntity<Boolean> deleteNotifications() throws Exception {
        return ResponseEntity.ok(notificationRecordService.deleteAllNotifications());
    }

    // Create new Record
    @PostMapping(value = "/records")
    public ResponseEntity<Boolean> createRecord(@RequestBody Records record) throws Exception {
        return ResponseEntity.ok(notificationRecordService.createRecord(record));
    }

    // Get all Records
    @GetMapping(value = "/records/query")
    public ResponseEntity<List<RecordEntity>> getAllRecords(@RequestParam("date") String dateStr) throws Exception {
        return ResponseEntity.ok(notificationRecordService.getAllRecords(dateStr));
    }


    // Count Records
    @GetMapping(value = "/records/count")
    public ResponseEntity<Long> getAllRecords() throws Exception {
        return ResponseEntity.ok(notificationRecordService.countRecords());
    }

    // Delete one record
    @DeleteMapping(value = "/records/{recordId}")
    public ResponseEntity<Boolean> deleteRecord(@PathVariable Long recordId) throws Exception {
        return ResponseEntity.ok(notificationRecordService.deleteRecordById(recordId));
    }

    // Delete all Records by Date
    @DeleteMapping(value = "/records/query")
    public ResponseEntity<Boolean> deleteAllRecords(@RequestParam("date") String dateStr) throws Exception {
        return ResponseEntity.ok(notificationRecordService.deleteAllRecordsByDate(dateStr));
    }
}
