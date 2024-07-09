package com.example.authentication.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Dictionary;
import java.util.List;

import com.example.authentication.exception.UserNotFoundException;
import com.example.authentication.model.Users;
import com.example.authentication.service.interfaces.UserService;

@CrossOrigin(origins = "http://localhost:8000")
@RestController 
@RequestMapping("/api")
public class UserController {
    @Autowired
    private final UserService userService;
    public UserController(UserService userService){
        this.userService = userService;
    }
    // Get all users
    @GetMapping(value = "/users")
    public ResponseEntity<List<Dictionary<String, String>>> getAllUsers(){
        return ResponseEntity.ok(userService.getAllUsers());
    }
    // Get User by Id
    @GetMapping(value = "/users/{id}")
    public ResponseEntity<Dictionary<String, String>> getUserById(@PathVariable("id") Long id) throws UserNotFoundException{
        return ResponseEntity.ok(userService.getUserById(id));
    }

    //Get User by Name
    @GetMapping(value= "/users/search")
    public ResponseEntity<List<Dictionary<String, Object>>> getUserByName(@RequestParam("userName") String userName) throws UserNotFoundException {
        return ResponseEntity.ok(userService.getUserByName(userName));
    }

    // Get User_id by User name
    @GetMapping(value = "/users/find")
    public ResponseEntity<Dictionary<String, Long>> getUserIdByUserName(@RequestParam("user_name") String userName) throws UserNotFoundException {
        return ResponseEntity.ok(userService.getUserIdByUserName(userName));
    }

    //Create new User
    @PostMapping(value = "/users")
    public ResponseEntity<Users> createUser(@RequestBody Users user) throws Exception{
        return ResponseEntity.ok(userService.createUsers(user));
    }

    // Update User
    @PatchMapping(value = "/users/{id}")
    public ResponseEntity<Users> updateUser(@PathVariable Long id, @RequestBody Users user) throws UserNotFoundException{
       return ResponseEntity.ok(userService.updateUser(id, user)); 
    }
    // Delete User By Id
    @DeleteMapping(value = "/users/{id}")
    public ResponseEntity<Boolean> deleteUser(@PathVariable Long id) throws UserNotFoundException{
        return ResponseEntity.ok(userService.deleteUser(id));
    }
}
