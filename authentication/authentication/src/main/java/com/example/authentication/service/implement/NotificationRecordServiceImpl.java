package com.example.authentication.service.implement;

import com.example.authentication.entity.NotificationEntity;
import com.example.authentication.entity.RecordEntity;
import com.example.authentication.model.Records;
import com.example.authentication.repository.NotificationRepository;
import com.example.authentication.repository.RecordRepository;
import com.example.authentication.service.interfaces.NotificationRecordService;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.NoSuchElementException;

@Service
@Transactional(rollbackOn = Exception.class)
@RequiredArgsConstructor
public class NotificationRecordServiceImpl implements NotificationRecordService {
    private final NotificationRepository notificationRepository;
    private final RecordRepository recordRepository;

    @Override
    public List<NotificationEntity> getAllNotifications() throws Exception {
        try {
            return notificationRepository.findAll();
        } catch (Exception e) {
            throw new Exception("Error retrieving notifications: " + e.getMessage(), e);
        }
    }

    @Override
    public List<RecordEntity> getAllRecords(String dateStr) throws Exception {
        try {
            return recordRepository.findAllRecordsByDateStr(dateStr).isPresent() ?
                    recordRepository.findAllRecordsByDateStr(dateStr).get() : null;
        } catch (Exception e) {
            throw new Exception("Error retrieving records: " + e.getMessage(), e);
        }
    }

    @Override
    public Boolean createNotification(String message) throws Exception {
        try {
            notificationRepository.save(new NotificationEntity(message));
            return true;
        } catch (Exception e) {
            throw new Exception("Error creating notification: " + e.getMessage(), e);
        }
    }

    @Override
    public Boolean createRecord(Records record) throws Exception {
        try {
            recordRepository.save(new RecordEntity(record.getRecordData(), record.getStatus()));
            return true;
        } catch (Exception e) {
            throw new Exception("Error creating record: " + e.getMessage(), e);
        }
    }

    @Override
    public Long countRecords() throws Exception {
        try {
            return recordRepository.countRecords();
        } catch (NoSuchElementException e) {
            throw new Exception("Could not count records: " + e.getMessage());
        }
    }
}
