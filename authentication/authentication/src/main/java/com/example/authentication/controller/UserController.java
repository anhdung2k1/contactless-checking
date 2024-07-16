package com.example.authentication.controller;

import com.example.authentication.model.Users;
import com.example.authentication.service.interfaces.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@CrossOrigin("*")
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;

    // Get all users
    @GetMapping(value = "/users")
    public ResponseEntity<List<Map<String, Object>>> getAllUsers() {
        return ResponseEntity.ok(userService.getAllUsers());
    }
    // Get User by Id
    @GetMapping(value = "/users/{id}")
    public ResponseEntity<Map<String, Object>> getUserById(@PathVariable("id") Long id) throws Exception{
        return ResponseEntity.ok(userService.getUserById(id));
    }

    //Get User by Name
    @GetMapping(value= "/users/search")
    public ResponseEntity<List<Map<String, Object>>> getUserByName(@RequestParam("userName") String userName) throws Exception {
        return ResponseEntity.ok(userService.getUserByName(userName));
    }

    // Get User_id by User name
    @GetMapping(value = "/users/find")
    public ResponseEntity<Map<String, Long>> getUserIdByUserName(@RequestParam("user_name") String userName) throws Exception {
        return ResponseEntity.ok(userService.getUserIdByUserName(userName));
    }

    //Create new User
    @PostMapping(value = "/users")
    public ResponseEntity<Users> createUser(@RequestBody Users user) throws Exception{
        return ResponseEntity.ok(userService.createUsers(user));
    }

    // Update User
    @PatchMapping(value = "/users/{id}")
    public ResponseEntity<Users> updateUser(@PathVariable Long id, @RequestBody Users user) throws Exception{
        return ResponseEntity.ok(userService.updateUser(id, user));
    }
    // Delete User By Id
    @DeleteMapping(value = "/users/{id}")
    public ResponseEntity<Map<String,Boolean>> deleteUser(@PathVariable Long id) throws Exception{
        return ResponseEntity.ok(new HashMap<>() {{
            put("deleted", userService.deleteUser(id));
        }});
    }
}