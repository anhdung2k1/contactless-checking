package com.example.authentication.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.authentication.entity.AccountEntity;

@Repository
public interface AccountRepository extends JpaRepository<AccountEntity,Long>{
    Optional<AccountEntity> findByUserName(String userName);
}
