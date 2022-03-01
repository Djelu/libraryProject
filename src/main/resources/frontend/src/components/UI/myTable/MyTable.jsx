import React from 'react';
import BooksCols from "../../BooksCols";
import BooksRows from "../../BooksRows";
import classes from "./MyTable.module.css"

const MyTable = ({cols, sortFoo, booksData}) => {
    const {resultBooks} = booksData;
    return (
        <div className={classes.items_container}>
            <BooksCols sortFoo={sortFoo} cols={cols}/>
            <BooksRows books={resultBooks} cols={cols}/>
        </div>
    );
};

export default MyTable;