package com.legalai.backend.Controller;

import com.legalai.backend.dto.AuthResponse;
import com.legalai.backend.dto.LoginRequest;
import com.legalai.backend.dto.RegisterRequest;
import com.legalai.backend.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/auth")
public class AuthController {
    private final AuthService service;

    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(@RequestBody RegisterRequest request){
        return ResponseEntity.ok(service.Register(request));
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@RequestBody LoginRequest request){
        return ResponseEntity.ok(service.login(request));
    }

    @GetMapping("/test")
    public String test(){
        return "test successfully protected endpoint";
    }

    @PostMapping("/admin")
    public ResponseEntity<AuthResponse> admin(@RequestBody RegisterRequest request){
        return ResponseEntity.ok(service.register_admin(request));
    }
}
