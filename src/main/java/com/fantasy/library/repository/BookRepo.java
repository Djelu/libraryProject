package com.fantasy.library.repository;

import com.fantasy.library.entity.BookEntity;
import org.springframework.data.repository.CrudRepository;

public interface BookRepo extends CrudRepository<BookEntity, Long> {
    BookEntity findByBookPageId(String bookPageId);
}
