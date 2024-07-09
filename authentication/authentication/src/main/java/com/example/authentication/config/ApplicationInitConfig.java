package com.example.authentication.config;

import com.example.authentication.model.Accounts;
import com.example.authentication.repository.AccountRepository;
import com.example.authentication.service.interfaces.AccountService;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
@Slf4j
public class ApplicationInitConfig {
    private final String DEFAULT_ADMIN = "admin";
    private final String DEFAULT_PASSWORD = "Admin@123";
    private final AccountRepository accountRepository;
    @Bean
    ApplicationRunner applicationRunner(AccountService accountService) {
        return args -> {
            if (accountRepository.findByUserName(DEFAULT_ADMIN).isPresent()) {
                log.warn("ADMIN user has been created before");
            } else {
                accountService.createAccount(new Accounts(DEFAULT_ADMIN, DEFAULT_PASSWORD));
                log.warn("ADMIN user has been created with default password: {}, please change it", DEFAULT_PASSWORD);
            }
        };
    }
}