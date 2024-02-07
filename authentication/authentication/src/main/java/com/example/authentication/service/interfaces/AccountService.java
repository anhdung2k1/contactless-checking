package com.example.authentication.service.interfaces;

import com.example.authentication.builder.AuthenticationResponse;
import com.example.authentication.exception.AccountNotFoundException;
import com.example.authentication.exception.UserNotFoundException;
import com.example.authentication.model.Accounts;
import java.util.*;

public interface AccountService {
    AuthenticationResponse createAccount(Accounts accounts) throws Exception;
    AuthenticationResponse authenticate(Accounts accounts) throws AccountNotFoundException;
    List<Accounts> getAllAccounts();
    boolean deleteAccount(Long id) throws AccountNotFoundException;
    Accounts getAccountsById(Long id) throws AccountNotFoundException;
    Long getAccIdByUserName (String userName) throws UserNotFoundException;
    Accounts updatePasswordAccount(Long id, Accounts accounts) throws AccountNotFoundException;
}
