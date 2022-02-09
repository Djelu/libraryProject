import React, {useEffect, useState} from 'react';

import BookService from "../API/BookService";
import {useFetching} from "../hooks/useFetching";
import {useBooks} from "../hooks/useBooks";
import BooksRows from "./BooksRows";
import BooksCols from "./BooksCols";
import HandledElem from "./HandledElem";
import MyTable from "./UI/myTable/MyTable";
import Filter from "./UI/filter/Filter";

const Books = () => {
    const cols = ["bookName", "imgUrl", "author", "genre", "year", "torUrl", "torSize", "bookDuration"];
    const getDefaultValues = function (){
        let result = {};
        cols.forEach(colName => result[colName] = null)
        return result
    }

    const [books, setBooks] = useState([]);
    const [booksData, setBooksData] = useState({sort: getDefaultValues(), filter: getDefaultValues()})
    const [limit, setLimit] = useState(10);
    const [page, setPage] = useState(1);

    const [fetchBooks, isBooksLoading, booksError] = useFetching(async (limit, page) => {
        const response = await BookService.getAll(limit, page);
        setBooks([...response.data])
    })

    useEffect(() => {
        fetchBooks(limit, page)
    }, [limit, page])

    const resultBooks = useBooks(books, booksData)

    const sortByCol = function (colName, isUp){
        let newSort = {...booksData.sort}
        newSort[colName] = isUp
        setBooksData({...booksData, sort: newSort})
    }

    const filterByCol = function (colName, value){
        let newFilter = {...booksData.filter}
        newFilter[colName] = value
        setBooksData({...booksData, filter: newFilter})
    }

    return (<div>
        <Filter cols={cols} filterFoo={filterByCol}/>
        <MyTable
            sortFoo={sortByCol}
            cols={cols}
            booksData={{
                resultBooks,
                isBooksLoading,
                booksError
            }}
        />
        {booksError
            ?<h1>Произошла ошибка ${booksError}</h1>
            :<div/>
        }
    </div>);
};

export default Books;