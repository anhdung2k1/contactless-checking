package com.example.authentication.service.interfaces;

import com.example.authentication.entity.NotificationEntity;
import com.example.authentication.entity.RecordEntity;
import com.example.authentication.model.Records;

import java.util.List;

public interface NotificationRecordService {
    List<NotificationEntity> getAllNotifications() throws Exception;
    Long countRecords() throws Exception;
    List<RecordEntity> getAllRecords(String dateStr) throws Exception;
    Boolean createNotification(String notifications) throws Exception;
    Boolean createRecord(Records record) throws Exception;
}