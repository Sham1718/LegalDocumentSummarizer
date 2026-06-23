package com.legalai.backend.repository;

import com.legalai.backend.entity.QueryHistory;

import com.legalai.backend.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

public interface QueryHistroyRepository extends JpaRepository<QueryHistory,Long> {
     Page<QueryHistory> findByUserOrderByCreatedAtDesc(User user, Pageable pageable);
}
