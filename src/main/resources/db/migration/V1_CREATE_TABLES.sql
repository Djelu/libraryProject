CREATE TABLE hibernate_sequence
(
    next_val bigint
) engine = MyISAM;

INSERT INTO hibernate_sequence
VALUES (1);
INSERT INTO hibernate_sequence
VALUES (1);

CREATE TABLE rutracker_books(
    id                 BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    book_page_id       VARCHAR(50) UNIQUE,
    url                VARCHAR(255),
    row_name           TEXT,
    book_name          VARCHAR(255),
    year               VARCHAR(255),
    last_name          VARCHAR(255),
    fist_name          VARCHAR(255),
    executor           VARCHAR(255),
    cycle_name         VARCHAR(255),
    book_number        VARCHAR(255),
    genre              TEXT,
    edition_type       VARCHAR(255),
    category           VARCHAR(255),
    audio_codec        VARCHAR(255),
    bitrate            VARCHAR(255),
    bitrate_type       VARCHAR(255),
    sampling_frequency VARCHAR(255),
    count_of_channels  VARCHAR(255),
    book_duration      VARCHAR(255),
    description        TEXT
); engine = MyISAM;
