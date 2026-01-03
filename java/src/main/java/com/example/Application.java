package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.HashMap;
import java.util.Map;

@SpringBootApplication
@RestController
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    @GetMapping("/")
    public Map<String, String> home() {
        Map<String, String> response = new HashMap<>();
        response.put("message", "Hello from Spring Boot!");
        response.put("environment", System.getenv().getOrDefault("SPRING_PROFILES_ACTIVE", "default"));
        return response;
    }

    @GetMapping("/api/info")
    public Map<String, String> info() {
        Map<String, String> response = new HashMap<>();
        response.put("app", "Spring Boot Application");
        response.put("version", "1.0.0");
        return response;
    }
}
