import React from 'react';
import Row from "./UI/row/Row";

const BooksRows = ({books, cols}) => {
    return (
        books.map((data, index) =>
            <Row key={data.bookPageId} data={data} cols={cols} index={index}/>
        )
    );
};

export default BooksRows;