package com.legalai.backend.service;

import com.legalai.backend.dto.AuthResponse;
import com.legalai.backend.dto.LoginRequest;
import com.legalai.backend.dto.RegisterRequest;
import com.legalai.backend.entity.Role;
import com.legalai.backend.entity.User;
import com.legalai.backend.repository.UserRepository;
import com.legalai.backend.security.CustomUserDetails;
import com.legalai.backend.security.JwtService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {
    private final UserRepository repository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager manager;
    private final JwtService jwtService;

    public AuthResponse Register(RegisterRequest request){

        User user= User.builder()
                .username(request.getUsername())
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .role(Role.User)
                .build();
        repository.save(user);

        CustomUserDetails userDetails = new CustomUserDetails(user);
        String token = jwtService.generateToken(user);
        return new AuthResponse(token);
    }

    public AuthResponse login(LoginRequest request){
        manager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        request.getEmail(),
                        request.getPassword()
                )
        );

        User user=repository.findByEmail(request.getEmail()).orElseThrow(()->new RuntimeException("User Not found"));

        CustomUserDetails userDetails = new CustomUserDetails(user);
        String token = jwtService.generateToken(user);
        return new AuthResponse(token);
    }

    public AuthResponse register_admin(RegisterRequest request){
        User user= User.builder()
                .username(request.getUsername())
                .email(request.getEmail())
                .password(request.getPassword())
                .role(Role.Admin)
                .build();
        repository.save(user);

        CustomUserDetails userDetails =new CustomUserDetails(user);
        String token = jwtService.generateToken(user);
        return new AuthResponse(token);

    }

    public Long getUserIdByEmail(String email) {

        return repository.findByEmail(email).map(User :: getId).orElseThrow(()->new RuntimeException("user not found"));
    }
    public String getEmailByUserId(Long userId){
        System.out.println("userID:"+userId);
        return repository.findById(userId).map(User:: getEmail).orElseThrow(()->new RuntimeException("no user found..!"));
    }
}
