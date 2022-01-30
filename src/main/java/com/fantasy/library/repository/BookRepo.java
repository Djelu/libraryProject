package com.fantasy.library.repository;

import com.fantasy.library.entity.BookEntity;
import org.springframework.data.repository.CrudRepository;

import java.util.List;

public interface BookRepo extends CrudRepository<BookEntity, Long> {
    BookEntity findByBookPageId(String bookPageId);
    List<BookEntity> findAll();
}
