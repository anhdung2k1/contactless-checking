package com.example.authentication.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import com.example.authentication.entity.UserEntity;

@Repository
public interface UserRepository extends JpaRepository<UserEntity, Long>{
    List<UserEntity> findByUserNameContains(String userName);
    
    @Query(value = "Select u.* from users u where u.user_name =:userName",nativeQuery=true)
    Optional<UserEntity> findByUserName(String userName);
}

