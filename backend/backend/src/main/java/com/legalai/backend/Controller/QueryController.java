package com.legalai.backend.Controller;

import com.legalai.backend.dto.AskRequest;
import com.legalai.backend.dto.AskResponse;
import com.legalai.backend.dto.QueryHistoryDto;
import com.legalai.backend.entity.User;
import com.legalai.backend.repository.QueryHistroyRepository;
import com.legalai.backend.security.CustomUserDetails;
import com.legalai.backend.service.RagClientService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;


@RestController
@RequestMapping("/api/query")
@CrossOrigin
public class QueryController {
    private final RagClientService ragClientService;
    private final QueryHistroyRepository histroyRepository;

    public QueryController(RagClientService ragClientService, QueryHistroyRepository histroyRepository) {
        this.ragClientService = ragClientService;
        this.histroyRepository = histroyRepository;
    }


    @PostMapping
    public ResponseEntity<AskResponse> ask(
            @RequestBody AskRequest request,
            Authentication authentication
    ) {
        CustomUserDetails userDetails =
                (CustomUserDetails) authentication.getPrincipal();
        User user = userDetails.getUser();
        AskResponse response =
                ragClientService.askQuestion(request.getQuestion(),request.getLanguage(),request.getTopK(), user);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/history")
    public ResponseEntity<Page<QueryHistoryDto>> history(
            Authentication authentication,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size
    ) {
        CustomUserDetails userDetails =
                (CustomUserDetails) authentication.getPrincipal();

        User user = userDetails.getUser();

        Page<QueryHistoryDto> response = ragClientService.getHistory(user,PageRequest.of(page,size));

        return ResponseEntity.ok(response);

    }


}
