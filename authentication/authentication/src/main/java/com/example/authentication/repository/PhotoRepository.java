package com.example.authentication.repository;

import com.example.authentication.entity.PhotoEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PhotoRepository extends JpaRepository<PhotoEntity, Long> {
}