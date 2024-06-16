package com.example.authentication.service.interfaces;

import com.example.authentication.exception.UserNotFoundException;
import com.example.authentication.model.Users;

import java.util.*;


public interface UserService {
    Users createUsers(Users user) throws Exception;
    List<Dictionary<String, String>> getAllUsers();
    Dictionary<String, String> getUserById(Long id) throws UserNotFoundException;
    List<Dictionary<String, Object>> getUserByName (String userName) throws UserNotFoundException;
    Dictionary<String, Long> getUserIdByUserName(String userName) throws UserNotFoundException;
    Users updateUser(Long id, Users user) throws UserNotFoundException;
    boolean deleteUser(Long id) throws UserNotFoundException;
}
