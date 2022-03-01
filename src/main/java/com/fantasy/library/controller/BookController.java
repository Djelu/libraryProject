package com.fantasy.library.controller;

import com.fantasy.library.service.BookService;
import com.fantasy.library.domain.Message;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

@CrossOrigin(origins = "*")
@RestController
@RequestMapping("/books")
public class BookController {

    @Autowired
    BookService bookService;

//    @GetMapping
//    public Flux<Message> list(
//            @RequestParam(defaultValue = "0") Long start,
//            @RequestParam(defaultValue = "3") Long count
//    ) {
//        return Flux
//                .just(
//                        "Hello, reactive!",
//                        "More then one",
//                        "Third post",
//                        "Fourth post",
//                        "Fifth post"
//                )
//                .skip(start)
//                .take(count)
//                .map(Message::new);
//    }

    @GetMapping("/getBooks")
    public Flux<String> getBooks(
            @RequestParam(defaultValue = "99999") long limit,
            @RequestParam(defaultValue = "1") long page){
        ObjectMapper mapper = new ObjectMapper();
        return Flux.just(bookService.getBooks())
                .skip((page-1)*limit)
                .take(limit)
                .mapNotNull(it -> {
                    try {
                        return mapper.writeValueAsString(it);
                    } catch (JsonProcessingException e) {
                        e.printStackTrace();
                    }
                    return null;
                });
    }
}
