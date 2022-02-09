package com.fantasy.library.entity;

import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;

import javax.persistence.*;

@Entity
@Table(name = "rutracker_books")
@NoArgsConstructor
public class BookEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Getter@Setter private String id;

    @Column(name="book_page_id")        @Getter@Setter private String bookPageId;
    @Column(name="row_name")            @Getter@Setter private String rowName;
    @Column(name="book_name")           @Getter@Setter private String bookName;
    @Column(name="last_name")           @Getter@Setter private String lastName;
    @Column(name="fist_name")           @Getter@Setter private String fistName;
    @Column(name="cycle_name")          @Getter@Setter private String cycleName;
    @Column(name="book_number")         @Getter@Setter private String bookNumber;
    @Column(name="edition_type")        @Getter@Setter private String editionType;
    @Column(name="audio_codec")         @Getter@Setter private String audioCodec;
    @Column(name="bitrate_type")        @Getter@Setter private String bitrateType;
    @Column(name="sampling_frequency")  @Getter@Setter private String samplingFrequency;
    @Column(name="count_of_channels")   @Getter@Setter private String countOfChannels;
    @Column(name="book_duration")       @Getter@Setter private String bookDuration;
    @Column(name="img_url")             @Getter@Setter private String imgUrl;
    @Column(name="magnet_link")         @Getter@Setter private String magnetLink;
    @Column(name="tor_size")            @Getter@Setter private String torSize;
    @Column(name="no_book")             @Getter@Setter private Boolean noBook;

    @Getter@Setter private String url;
    @Getter@Setter private String year;
    @Getter@Setter private String executor;
    @Getter@Setter private String genre;
    @Getter@Setter private String category;
    @Getter@Setter private String bitrate;
    @Getter@Setter private String description;
}
