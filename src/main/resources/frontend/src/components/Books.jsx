import React, {useEffect, useState} from 'react';

import BookService from "../API/BookService";
import {useFetching} from "../hooks/useFetching";
import {useBooks} from "../hooks/useBooks";
import BooksRows from "./BooksRows";
import BooksCols from "./BooksCols";
import HandledElem from "./HandledElem";

const Books = () => {
    const cols = ["book_name", "author", "genre", "year", "book_duration"];
    const getDefaultSort = function (){
        let result = {};
        cols.forEach(colName => result[colName] = null)
        return result
    }

    const [books, setBooks] = useState([]);
    const [filter, setFilter] = useState({sort: getDefaultSort(), query: ''})
    const [limit, setLimit] = useState(10);
    const [page, setPage] = useState(1);

    const [fetchBooks, isBooksLoading, booksError] = useFetching(async (limit, page) => {
        const response = await BookService.getAll(limit, page);
        setBooks([...response])
    })

    useEffect(() => {
        fetchBooks(limit, page)
    }, [limit, page])

    const resultBooks = useBooks(books, filter)

    const sortByRow = function (colName, isUp){
        let newSort = {...filter.sort}
        newSort[colName] = isUp
        setFilter({...filter, sort: newSort})
    }

    return (
        <table>
            <thead>
                <BooksCols sortFoo={sortByRow} cols={cols}/>
            </thead>
            <tbody>
                <HandledElem isLoading={isBooksLoading} error={booksError}>
                    <BooksRows books={resultBooks} cols={cols}/>
                </HandledElem>
            </tbody>
        </table>
    );
};

export default Books;