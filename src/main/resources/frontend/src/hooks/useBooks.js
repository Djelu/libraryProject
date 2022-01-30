import {useMemo} from "react";
import ConvertingService from "../API/ConvertingService";

export const useSortedBooks = (books, sort) => {
    return useMemo(() => {
        const sortCols = Object.keys(sort).filter(k => sort[k] != null);
        if (sortCols.length === 0)
            return books;

        return [...books.sort((book1, book2) => {
            for (const key of sortCols) {
                const result = getCompareResult(book1, book2, sort, key);
                if (result !== 0) {
                    return result;
                }
            }
        })]
    }, [sort, books]);
}

const getCompareResult = (book1, book2, sort, key) => {
    const isUp = sort[key];

    const depKeys = ConvertingService.getColDepends(key)
    let result;
    if (depKeys.length === 1 && depKeys.includes(key)) {
        result = compareWithDirection(book1[key], book2[key], isUp);
    } else {
        result = compareWithDirection(
            getSumOfValues(book1, depKeys),
            getSumOfValues(book2, depKeys),
            isUp
        );
    }
    return result;
}

const compareWithDirection = (a, b, isUp) => {
    return isUp
        ? a.localeCompare(b)
        : b.localeCompare(a)
}

const getSumOfValues = (data, keys) => {
    return keys.map(k => data[k]).join(" ")
}

export const useBooks = (books, filter) => {
    const {sort, query} = filter;
    const sortedPosts = useSortedBooks(books, sort)

    return useMemo(() => {
        return sortedPosts.filter(book => book.book_name.includes(query))
    }, [query, sortedPosts]);
}