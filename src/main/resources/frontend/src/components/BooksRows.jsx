import React from 'react';
import Row from "./UI/row/Row";

const BooksRows = ({books, cols}) => {
    return (
        books.map((data, index) =>
            <Row key={data.book_page_id} data={data} cols={cols} index={index}/>
        )
    );
};

export default BooksRows;