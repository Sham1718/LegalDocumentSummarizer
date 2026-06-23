package com.legalai.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
@AllArgsConstructor
public class AskResponse {
    private String answer;
    private String explanation;
    private List<String> sources;
    private List<Object> evidence_chunks;
    private String language;


}
