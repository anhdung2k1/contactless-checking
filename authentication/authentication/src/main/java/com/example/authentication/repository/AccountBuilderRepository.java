package com.example.authentication.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.authentication.builder.AccountBuilder;

@Repository
public interface AccountBuilderRepository extends JpaRepository<AccountBuilder, Long>{
    Optional<AccountBuilder> findByUserName(String userName);
}
