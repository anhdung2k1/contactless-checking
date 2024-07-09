package com.example.authentication.controller;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.example.authentication.builder.AuthenticationResponse;
import com.example.authentication.exception.AccountNotFoundException;
import com.example.authentication.exception.UserNotFoundException;
import com.example.authentication.model.Accounts;
import com.example.authentication.service.interfaces.AccountService;

@CrossOrigin(origins = "http://localhost:8000")
@RestController
@RequestMapping("/api")
public class AccountController {
    @Autowired
    private final AccountService accountService;

    public AccountController(AccountService accountService){
        this.accountService = accountService;
    }

    //Sign Up new account
    @PostMapping(value="/accounts/signup")
    public ResponseEntity<AuthenticationResponse> createAccount(@RequestBody Accounts account) throws Exception {
        return ResponseEntity.ok(accountService.createAccount(account));
    }
    //Sign In account
    @PostMapping(value="/accounts/signin")
    public ResponseEntity<AuthenticationResponse> authenticate(@RequestBody Accounts account) throws AccountNotFoundException{
        return ResponseEntity.ok(accountService.authenticate(account));
    }
    //Get all account
    @GetMapping(value = "/accounts")
    public ResponseEntity<List<Accounts>> getAllAccounts(){
        return ResponseEntity.ok(accountService.getAllAccounts());
    }
    //Get Account by ID
    @GetMapping(value = "/accounts/{id}")
    public ResponseEntity<Accounts> getAccountById(@PathVariable Long id) throws AccountNotFoundException {
        return ResponseEntity.ok(accountService.getAccountsById(id));
    }

    // Get account id by user id
    @GetMapping(value = "/accounts/find")
    public ResponseEntity<Long> getAccIdByUserName (@RequestParam("userName") String userName) throws UserNotFoundException {
        return ResponseEntity.ok(accountService.getAccIdByUserName(userName));
    }

    //Put Account Change Password
    @PutMapping(value = "/accounts/{id}")
    public ResponseEntity<Accounts> updateAccountPassword(@PathVariable Long id, @RequestBody Accounts account) throws AccountNotFoundException{
        return ResponseEntity.ok(accountService.updatePasswordAccount(id, account));
    }
    //Delete Account
    @DeleteMapping(value = "/accounts/{id}")
    public ResponseEntity<Map<String,Boolean>> deleteAccount(@PathVariable Long id) throws AccountNotFoundException{
        boolean deleted = accountService.deleteAccount(id);
        Map<String, Boolean> response = new HashMap<>();
        response.put("deleted", deleted);
        return ResponseEntity.ok(response);
    }
}
