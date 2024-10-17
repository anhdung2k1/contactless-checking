package com.example.authentication.config;

import java.util.Arrays;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import lombok.RequiredArgsConstructor;

@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfiguration {

    private static final Logger logger = LoggerFactory.getLogger(SecurityConfiguration.class);

    private final JwtAuthenticationFilter jwtAuthenticationFilter;
    private final AuthenticationProvider authenticationProvider;

    @Value("${cors.allowed-origins:http://localhost}")
    private String[] allowedOrigins;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        logger.info("Setting up security filter chain...");
        
        SecurityFilterChain filterChain = http
                .cors(cors -> cors.configurationSource(corsConfigurationSource()))  // Apply CORS configuration
                .csrf(csrf -> csrf.disable())  // Disable CSRF for stateless authentication
                .authorizeHttpRequests(requests -> requests
                        .requestMatchers("/api/accounts/signin", "/api/accounts/signup", "/actuator/**").permitAll()  // Public routes
                        .anyRequest().authenticated())  // Protect other routes
                .sessionManagement(session -> session
                        .sessionCreationPolicy(SessionCreationPolicy.STATELESS))  // Stateless session management
                .authenticationProvider(authenticationProvider)
                .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)  // Add JWT filter
                .build();
        
        logger.info("Security filter chain configured successfully.");
        
        return filterChain;
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        logger.info("Setting up CORS configuration...");

        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(Arrays.asList(allowedOrigins));  // Allow the specific origins
        logger.info("Allowed Origins: {}", Arrays.toString(allowedOrigins));
        configuration.setAllowedMethods(Arrays.asList("HEAD", "GET", "POST", "PUT", "DELETE", "PATCH", "OPTION"));  // Allow necessary methods
        logger.info("Allowed Methods: {}", configuration.getAllowedMethods());
        configuration.setAllowedHeaders(Arrays.asList("Authorization", "Content-Type", "Accept"));  // Allow specific headers
        logger.info("Allowed Headers: {}", configuration.getAllowedHeaders());
        configuration.setExposedHeaders(Arrays.asList("Authorization"));  // Expose Authorization in the response headers
        logger.info("Exposed Headers: {}", configuration.getExposedHeaders());
        configuration.setAllowCredentials(true);  // Allow credentials (cookies, Authorization headers)
        logger.info("Allow Credentials: {}", configuration.getAllowCredentials());
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);  // Apply CORS configuration to all paths
        logger.info("CORS configuration source setup successfully.");

        return source;
    }
}
