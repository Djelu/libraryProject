package com.fantasy.library.model;
import com.fantasy.library.entity.BookEntity;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.SneakyThrows;

import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import java.lang.reflect.Field;
import java.util.Arrays;
import java.util.function.Consumer;

@NoArgsConstructor
public class Book {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Getter@Setter private String id;

    @Getter@Setter private String bookPageId;
    @Getter@Setter private String rowName;
    @Getter@Setter private String bookName;
    @Getter@Setter private String lastName;
    @Getter@Setter private String fistName;
    @Getter@Setter private String cycleName;
    @Getter@Setter private String bookNumber;
    @Getter@Setter private String editionType;
    @Getter@Setter private String audioCodec;
    @Getter@Setter private String bitrateType;
    @Getter@Setter private String samplingFrequency;
    @Getter@Setter private String countOfChannels;
    @Getter@Setter private String bookDuration;
    @Getter@Setter private String url;
    @Getter@Setter private String year;
    @Getter@Setter private String executor;
    @Getter@Setter private String genre;
    @Getter@Setter private String category;
    @Getter@Setter private String bitrate;
    @Getter@Setter private String description;
    @Getter@Setter private String imgUrl;
    @Getter@Setter private String magnetLink;
    @Getter@Setter private String torSize;
    @Getter@Setter private Boolean noBook;

    public static Book toModel(BookEntity entity) throws NoSuchFieldException, IllegalAccessException {
        Book book = new Book();
        for(Field entityField: entity.getClass().getDeclaredFields()) {
            entityField.setAccessible(true);
            final Field bookField = book.getClass().getDeclaredField(entityField.getName());
            bookField.setAccessible(true);
            bookField.set(book, entityField.get(entity));
        }
        return book;
    }
}
