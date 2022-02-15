import React from 'react';
import BooksCols from "../../BooksCols";
import HandledElem from "../../HandledElem";
import BooksRows from "../../BooksRows";
import classes from "./MyTable.module.css";

const MyTable = ({cols, sortFoo, booksData}) => {
    const {resultBooks} = booksData;
    return (
        <div>
            <table className={classes.foo}>
                <thead>
                <BooksCols sortFoo={sortFoo} cols={cols}/>
                </thead>
                <tbody>
                </tbody>
            </table>
            <BooksRows books={resultBooks} cols={cols}/>
        </div>
    );
};

export default MyTable;