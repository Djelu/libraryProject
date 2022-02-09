package com.fantasy.library;

import com.fantasy.library.model.Book;
import com.fantasy.library.repository.BookRepo;
import lombok.SneakyThrows;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Objects;

@Service
public class BookService {

    @Autowired
    private BookRepo bookRepo;

    @SneakyThrows
    public List<Book> getBooks() {
        return bookRepo.findAll()
                .stream()
                .filter(entity -> !entity.getNoBook())
                .map(entity -> {
                    try {
                        return Book.toModel(entity);
                    } catch (NoSuchFieldException | IllegalAccessException e) {
                        e.printStackTrace();
                    }
                    return null;
                })
                .filter(Objects::nonNull)
                .toList();
    }
}
