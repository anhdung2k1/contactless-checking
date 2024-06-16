package com.example.authentication.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

@ResponseStatus(code = HttpStatus.NOT_FOUND, reason = "User is not found")
public class UserNotFoundException  extends Exception{
    public UserNotFoundException(String message){
        super(message);
    }
}
