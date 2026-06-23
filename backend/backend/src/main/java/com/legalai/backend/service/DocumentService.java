package com.legalai.backend.service;

import com.legalai.backend.dto.DocumentResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.client.WebClient;

import java.io.File;
import java.io.IOException;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class DocumentService {
    private final WebClient webClient;

    public DocumentResponse process(MultipartFile file)
            throws IOException {

        File tempFile = File.createTempFile(
                "legal_", "_" + file.getOriginalFilename()
        );
        file.transferTo(tempFile);

        DocumentResponse response = webClient.post()
                .uri("/document/process")
                .bodyValue(Map.of(
                        "path", tempFile.getAbsolutePath()
                ))
                .retrieve()
                .bodyToMono(DocumentResponse.class)
                .block();

        tempFile.delete(); // cleanup
        return response;
    }
}
