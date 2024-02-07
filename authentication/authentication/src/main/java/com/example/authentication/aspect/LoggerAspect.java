package com.example.authentication.aspect;

import java.time.Duration;
import java.time.Instant;

import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.AfterThrowing;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Configuration;

import jakarta.validation.constraints.NotNull;

@Configuration
@Aspect
public class LoggerAspect {
    private Logger logger = LoggerFactory.getLogger(LoggerAspect.class);
    @Around("execution(* com.example.authentication.*.*(..))")
    public Object before(@NotNull ProceedingJoinPoint joinPoint) throws Throwable{
        logger.info(joinPoint.getSignature().toString() + "method start");
        Instant startTime = Instant.now();
        Object result = joinPoint.proceed(); // Snap the time when running
        Instant endTime = Instant.now();
        long timeProcess = Duration.between(startTime, endTime).toMillis();
        logger.info("Time excecuted: " + joinPoint.getSignature().toString() + "running end "+ timeProcess);
        logger.info(joinPoint.getSignature().toString() + "end");
        return result;
    }
    @AfterThrowing(value = "execution(* com.example.authentication.*.*(..))", throwing = "e")
    public void logException(@NotNull JoinPoint joinPoint, @NotNull Exception e){
        logger.error(joinPoint.getSignature().toString() + "An exception happend because of " + e.getMessage());
    }
}
