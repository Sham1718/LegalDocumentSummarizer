package com.legalai.backend.service;

import com.legalai.backend.dto.AskRequest;
import com.legalai.backend.dto.AskResponse;
import com.legalai.backend.dto.QueryHistoryDto;
import com.legalai.backend.entity.QueryHistory;

import com.legalai.backend.entity.User;
import com.legalai.backend.repository.QueryHistroyRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.Duration;

@Service
public class RagClientService {

    private final WebClient webClient;
    private final QueryHistroyRepository queryHistroyRepository;

    public RagClientService(WebClient webClient,  QueryHistroyRepository queryHistroyRepository) {
        this.webClient = webClient;
        this.queryHistroyRepository = queryHistroyRepository;

    }

    public AskResponse askQuestion(String question, String language, Integer topK, User user) {
//        AskRequest payload = new AskRequest(
//                question,
//                language != null ? language : "en",
//                topK != null ? topK : 5
//        );

        AskResponse response = webClient.post()
                .uri("/ask")
                .bodyValue(new AskRequest(question,language,topK))
                .retrieve()
                .bodyToMono(AskResponse.class)
                .timeout(Duration.ofSeconds(25))
                .onErrorMap(err -> new RuntimeException("RAG API failed", err))
                .block();

        // ---- Persist query ----
        QueryHistory history = new QueryHistory();
        history.setQuestion(question);
        history.setAnswer(response.getAnswer());
//        System.out.println(response.getAnswer());
        history.setUser(user);

        if (response.getSources() != null) {
            history.setSources(
                    String.join(",",response.getSources())
            );
        }
        queryHistroyRepository.save(history);
        return response;
    }



    public Page<QueryHistoryDto> getHistory(User user, PageRequest pageRequest) {

        Page<QueryHistory> history =
                queryHistroyRepository.findByUserOrderByCreatedAtDesc(
                        user, pageRequest
                );

        return history.map(h -> new QueryHistoryDto(
                h.getQuestion(),
                h.getAnswer(),
                h.getSources(),
                h.getCreatedAt()
        ));
    }
}
