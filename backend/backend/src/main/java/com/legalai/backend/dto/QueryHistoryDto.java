package com.legalai.backend.dto;

import jakarta.persistence.Column;
import jakarta.persistence.Lob;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
@AllArgsConstructor
public class QueryHistoryDto {
    private String question;
    @Lob
    @Column(columnDefinition = "LONGTEXT")
    private String answer;
    private String sources;
    private LocalDateTime createdAt;
}
