package com.example.authentication.service.implement;

import java.time.LocalDateTime;
import java.util.*;

import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;

import com.example.authentication.entity.UserEntity;
import com.example.authentication.exception.UserNotFoundException;
import com.example.authentication.model.Users;
import com.example.authentication.repository.UserRepository;
import com.example.authentication.service.interfaces.UserService;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;

@Service
@Transactional(rollbackOn = Exception.class)
@RequiredArgsConstructor
public class UserServiceImpl implements UserService{

    private final UserRepository userRepository;

    @Override
    public Users createUsers(Users user) throws Exception{
        try{
            UserEntity userEntity = new UserEntity();
            user.setCreateAt(LocalDateTime.now());
            user.setUpdateAt(LocalDateTime.now());
            BeanUtils.copyProperties(user, userEntity);
            userRepository.save(userEntity);
            return user;
        }
        catch(Exception e) {
            throw new Exception(e.getMessage());
        }
    }

    @Override
    public boolean deleteUser(Long id) throws UserNotFoundException {
       try{
            UserEntity userEntity = userRepository.findById(id).isPresent() ? userRepository.findById(id).get() : null;
            assert userEntity != null;
            userRepository.delete(userEntity);
            return true; 
       }catch(NoSuchElementException e){
            throw new UserNotFoundException("User is not found :%d" + id.toString());
       }
    }

    @Override
    public List<Dictionary<String, String>> getAllUsers() {
        List<UserEntity> userEntities = userRepository.findAll();
        List<Dictionary<String, String>> output = new ArrayList<Dictionary<String, String>>();
        for (UserEntity userEntity: userEntities) {
            Dictionary<String, String> user = new Hashtable<>();
            
            user.put("name", userEntity.getUserName());

            output.add(user);
        }
        return output;
    }

    @Override
    public Dictionary<String, String> getUserById(Long id) throws UserNotFoundException {
        try {
            UserEntity userEntity = userRepository.findById(id).isPresent() ? userRepository.findById(id).get() : null;
            // Assign all the properties USER Properties to users
            assert userEntity != null;
            Dictionary<String, String> output = new Hashtable<>();
            output.put("userName", userEntity.getUserName());
            output.put("address", userEntity.getAddress());
            output.put("gender", userEntity.getGender());
            return output;
        }
        catch (NoSuchElementException e){
            throw new UserNotFoundException("User is not found :%d" + id.toString());
        }
    }

    @Override
    public List<Dictionary<String, Object>> getUserByName(String userName) throws UserNotFoundException {
        List<UserEntity> userEntities = userRepository.findByUserNameContains(userName);
        List<Dictionary<String, Object>> output = new ArrayList<Dictionary<String, Object>>();
        for (UserEntity userEntity: userEntities) {
            Dictionary<String, Object> user = new Hashtable<>();
            
            user.put("userId", userEntity.getUser_id());
            user.put("userName", userEntity.getUserName());
            output.add(user);
        }
        return output;
    }

    @Override
    public Dictionary<String, Long> getUserIdByUserName(String userName) throws UserNotFoundException {
        try {
            UserEntity userEntity = userRepository.findByUserName(userName).get();
            Dictionary<String, Long> output = new Hashtable<>();
            output.put("user_id", userEntity.getUser_id());
            return output;
        }
        catch (NoSuchElementException e){
            throw new UserNotFoundException("User is not found :%d");
        }

    }

    @Override
    public Users updateUser(Long id, Users user) throws UserNotFoundException {
        try{
            UserEntity userEntity = userRepository.findById(id).isPresent() ? userRepository.findById(id).get() : null;
            assert userEntity != null;
            userEntity.setAddress(user.getAddress());
            userEntity.setBirth_day(user.getBirth_day());
            userEntity.setGender(user.getGender());
            userEntity.setUpdateAt(LocalDateTime.now());
            return user;
        }
        catch (NoSuchElementException e){
            throw new UserNotFoundException("User is not found :%d" + id.toString());
        }
    }
}
