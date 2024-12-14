package com.example.authentication.aspect;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class Utils {
    private static final SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
    public static String dateToString(Date date) {
        return dateFormat.format(date);
    }

    public static Date stringToDate(String dateStr) {
        try {
            if (!dateStr.isEmpty() && dateStr.matches("^\\d{4}-\\d{2}-\\d{2}$")) {
                return dateFormat.parse(dateStr);
            }
        } catch (ParseException e) {
            log.error("Error parsing date: " + e.getMessage());
        }
        return null;
    }
}