package com.example.authentication.repository;

import com.example.authentication.entity.RecordEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface RecordRepository extends JpaRepository<RecordEntity, Long> {
    @Query(value = "SELECT rc.* FROM records rc " +
            "WHERE rc.create_at LIKE CONCAT ('%', :dateStr, '%')", nativeQuery = true)
    Optional<List<RecordEntity>> findAllRecordsByDateStr(String dateStr);

    @Query(value = "SELECT COUNT(1) FROM records", nativeQuery = true)
    Long countRecords();
}