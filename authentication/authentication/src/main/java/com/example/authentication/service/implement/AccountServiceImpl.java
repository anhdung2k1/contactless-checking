package com.example.authentication.service.implement;

import java.time.LocalDateTime;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.stream.Collectors;

import org.springframework.beans.BeanUtils;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import com.example.authentication.builder.AccountBuilder;
import com.example.authentication.builder.AuthenticationResponse;
import com.example.authentication.config.JwtService;
import com.example.authentication.entity.AccountEntity;
import com.example.authentication.entity.UserEntity;
import com.example.authentication.exception.AccountNotFoundException;
import com.example.authentication.exception.UserNotFoundException;
import com.example.authentication.model.Accounts;
import com.example.authentication.repository.AccountBuilderRepository;
import com.example.authentication.repository.AccountRepository;
import com.example.authentication.repository.UserRepository;
import com.example.authentication.service.interfaces.AccountService;

import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@Transactional(rollbackOn = Exception.class)
@RequiredArgsConstructor
@Slf4j
public class AccountServiceImpl implements AccountService {
    private final AccountRepository accountRepository;
    private final AccountBuilderRepository accountBuilderRepository;
    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;
    private final UserRepository userRepository;
    private final AuthenticationManager authenticationManager;

    @Override
    public AuthenticationResponse authenticate(Accounts accounts) throws AccountNotFoundException {
        try {
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(accounts.getUserName(), accounts.getPassword()));
            SecurityContextHolder.getContext().setAuthentication(authentication);
            AccountBuilder account = accountBuilderRepository.findByUserName(accounts.getUserName()).orElseThrow();
            var jwtToken = jwtService.generateToken(account);
            var expireDate = jwtService.extractExpiration(jwtToken);

            return AuthenticationResponse.builder()
                    .token(jwtToken)
                    .expireDate(expireDate)
                    .userName(accounts.getUserName())
                    .build();
        } catch (NoSuchElementException e) {
            throw new AccountNotFoundException(String.format("Account is existed"));
        }
    }

    @Override
    public AuthenticationResponse createAccount(Accounts accounts) throws Exception {
        try {
            AccountEntity accountEntity = new AccountEntity();
            if (accountRepository.findByUserName(accounts.getUserName()).isPresent()) {
                throw new Exception("User exists");
            }
            String encodedPassword = passwordEncoder.encode(accounts.getPassword());
            accounts.setPassword(encodedPassword);
            accounts.setCreateAt(LocalDateTime.now());
            accounts.setUpdateAt(LocalDateTime.now());
            // Create new User when adding new account into database
            UserEntity users = new UserEntity(accounts.getUserName());
            users.setAddress("UNKNOWN");
            users.setGender("UNKNOWN");
            userRepository.save(users);
            log.info("Save User: {}", users);
            accounts.setUsers(users);
            BeanUtils.copyProperties(accounts, accountEntity);
            accountRepository.save(accountEntity);
            log.info("Save Account: {}", accountEntity);
            var user = AccountBuilder.builder()
                    .userName(accounts.getUserName())
                    .password(encodedPassword)
                    .createAt(accounts.getCreateAt())
                    .updateAt(accounts.getUpdateAt())
                    .build();
            var jwtToken = jwtService.generateToken(user);
            var expireDate = jwtService.extractExpiration(jwtToken);

            return AuthenticationResponse.builder()
                    .token(jwtToken)
                    .expireDate(expireDate)
                    .userName(accounts.getUserName())
                    .build();
        } catch (Exception e) {
            throw new Exception(e.getMessage());
        }
    }

    @Override
    public boolean deleteAccount(Long id) throws AccountNotFoundException {
        try {
            AccountEntity accountEntity = accountRepository.findById(id).isPresent()
                    ? accountRepository.findById(id).get()
                    : null;
            assert accountEntity != null;
            accountRepository.delete(accountEntity);
            return true;
        } catch (NoSuchElementException e) {
            throw new AccountNotFoundException(String.format("Could not find any account within id: %s", id));
        }
    }

    @Override
    public Accounts getAccountsById(Long id) throws AccountNotFoundException {
        try {
            AccountEntity accountsEntity = accountRepository.findById(id).isPresent()
                    ? accountRepository.findById(id).get()
                    : null;
            Accounts account = new Accounts();
            assert accountsEntity != null;
            BeanUtils.copyProperties(accountsEntity, account);
            return account;
        } catch (NoSuchElementException e) {
            throw new AccountNotFoundException(String.format("Could not find any account within id: %s", id));
        }
    }

    @Override
    public List<Accounts> getAllAccounts() {
        List<AccountEntity> accountsEntities = accountRepository.findAll();
        return accountsEntities.stream()
                .map(acc -> new Accounts(
                        acc.getAcc_id(),
                        acc.getUserName(),
                        acc.getPassword(),
                        acc.getPhone_number(),
                        acc.getUsers(),
                        acc.getCreateAt(),
                        acc.getUpdateAt()))
                .collect(Collectors.toList());
    }

    @Override
    public Long getAccIdByUserName(String userName) throws UserNotFoundException {
        try {
            UserEntity userEntity = userRepository.findByUserName(userName).isPresent()
                    ? userRepository.findByUserName(userName).get()
                    : null;
            assert userEntity != null;
            AccountEntity accountEntity = accountRepository.findByUserName(userName).get();
            return accountEntity.getAcc_id();
        } catch (NoSuchElementException e) {
            throw new UserNotFoundException("User is not found :%d");
        }
    }

    @Override
    public Accounts updatePasswordAccount(Long id, Accounts accounts) throws AccountNotFoundException {
        try {
            AccountEntity accountEntity = accountRepository.findById(id).isPresent()
                    ? accountRepository.findById(id).get()
                    : null;
            assert accountEntity != null;
            if (accounts.getPassword() == null) {
                throw new AccountNotFoundException("Password editing must not be null");
            } else {
                accountEntity.setPassword(passwordEncoder.encode(accounts.getPassword()));
                accountEntity.setCreateAt(LocalDateTime.now());
                accountEntity.setUpdateAt(LocalDateTime.now());
                accountRepository.save(accountEntity);
                return accounts;
            }
        } catch (NoSuchElementException e) {
            throw new AccountNotFoundException(String.format("Could not find any account within id: %s", id));
        }
    }

}
