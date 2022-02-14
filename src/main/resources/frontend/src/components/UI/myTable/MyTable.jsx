import React from 'react';
import BooksCols from "../../BooksCols";
import HandledElem from "../../HandledElem";
import BooksRows from "../../BooksRows";
import classes from "./MyTable.module.css";

const MyTable = ({cols, sortFoo, booksData}) => {
    const {resultBooks, isBooksLoading, booksError} = booksData;
    return (
        <table className={classes.foo}>
            <thead>
                <BooksCols sortFoo={sortFoo} cols={cols}/>
            </thead>
            <tbody>
                <BooksRows books={resultBooks} cols={cols}/>
            </tbody>
        </table>
    );
};

export default MyTable;