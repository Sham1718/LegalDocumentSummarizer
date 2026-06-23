package com.legalai.backend.Controller;

import com.legalai.backend.dto.DocumentResponse;
import com.legalai.backend.service.DocumentService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@RequestMapping("/api/document")
@CrossOrigin
@RequiredArgsConstructor
public class DocumentController {
    private final DocumentService service;

    @PostMapping("/upload")
    public ResponseEntity<DocumentResponse> upload(
            @RequestParam("file") MultipartFile file
    ) throws IOException {
        if (file.isEmpty()){
            return ResponseEntity.badRequest().build();
        }
        DocumentResponse response=service.process(file);
        return ResponseEntity.ok(response);
    }
}
