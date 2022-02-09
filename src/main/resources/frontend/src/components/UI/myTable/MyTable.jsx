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
                <HandledElem isLoading={isBooksLoading} error={booksError}>
                    <BooksRows books={resultBooks} cols={cols}/>
                </HandledElem>
            </tbody>
        </table>
    );
};

export default MyTable;