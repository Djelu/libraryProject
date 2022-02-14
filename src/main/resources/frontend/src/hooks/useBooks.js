import {useMemo} from "react";
import ConvertingService from "../API/ConvertingService";

const useFilteredBooks = (books, filter, filterType) => {
    return useMemo(() => {
        const filterCols = Object.keys(filter).filter(k => filter[k] != null);
        if (filterCols.length === 0)
            return books;
        return [...books.filter(book => {
            for (const colName of filterCols) {
                const bookValue = ConvertingService.getValueFromBook(book, colName);
                if(!filterWasPassed(bookValue, filter[colName], filterType[colName], colName))
                    return false;
            }
            return true;
        })]
    }, [filter, filterType, books])
}

const filterWasPassed = (bookValue, filterValue, filterTypeIsStraight, colName) => {
    if(!filterValue)return true;
    const passed = filterTypeIsStraight
        ? (val1, val2) => val1.includes(val2)
        : (val1, val2) => !val1.includes(val2);
    switch (colName){
        case "author":
            const val1 = bookValue.toLowerCase();
            return filterValue.split(" ").every(fVal => passed(val1, fVal.toLowerCase()));
        default: {
            return passed(bookValue.toLowerCase(), filterValue.toLowerCase());
        }
    }
}

const useSortedBooks = (books, sort) => {
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
        result = compareValues(book1[key], book2[key], isUp, key);
    } else {
        result = compareValues(
            getSumOfValues(book1, depKeys),
            getSumOfValues(book2, depKeys),
            isUp,
            key
        );
    }
    return result;
}

const compareValues = (a, b, isUp, colName) => {
    // if (colName == "bookDuration" && a!=null && b!=null && b.split(":").length > 3)
    //     debugger;
    switch (colName) {
        case "torSize":
            const nbsp = String.fromCharCode(160);
            if(a == null || a.indexOf(nbsp) === -1)
                a = "0"+nbsp+"KB";
            if(b == null || b.indexOf(nbsp) === -1)
                b = "0"+nbsp+"KB";
            const sizeA = a.split(nbsp);
            const sizeB = b.split(nbsp);
            if (sizeA.length !== 2 || sizeB.length !== 2)
                return 0;
            return compareWithDirection(
                ConvertingService.getKBValue(sizeA[0], sizeA[1]),
                ConvertingService.getKBValue(sizeB[0], sizeB[1]),
                isUp,
                colName
            );
        case "bookDuration":
            if(a == null || a.indexOf(":") === -1)
                a = "0";
            if(b == null || b.indexOf(":") === -1)
                b = "0";
            return compareWithDirection(
                getRightDuration(a, isUp, colName),
                getRightDuration(b, isUp, colName),
                isUp,
                colName
            );
    }

    return compareWithDirection(a, b, isUp, colName);
}

const getRightDuration = (value, isUp, colName) => {
    if(value.indexOf(";") === -1 && value.indexOf("+") === -1)
        return value.replaceAll(":", "");
    const durArr = value.split(";")
        .flatMap(val => val.split("+"))
        .map(val => val.trim())
        .sort((a, b) => compareWithDirection(
            a.replaceAll(":", ""),
            b.replaceAll(":", ""),
            isUp,
            colName
        ));
    return isUp ?durArr[0] :durArr[durArr.length - 1];
}

const compareWithDirection = (a, b, isUp, colName) => {
    switch (colName){
        case "year":
        case "torSize":
        case "bookDuration":
            return isUp
                ? a - b
                : b - a;
        default:
            return isUp
                ? a.localeCompare(b)
                : b.localeCompare(a);
    }
}

const compareWithNullCheck = (a, b, foo) => {
    if(a == null && b == null)
        return 0;
    else if(a == null)
        return -1;
    else if(b == null)
        return 1;
    else
        return foo();
}

const getSumOfValues = (data, keys) => {
    return keys.map(k => data[k]).join(" ")
}

export const useBooks = (books, booksData) => {
    const {sort, filter, filterType} = booksData;
    const sortedBooks = useSortedBooks(books, sort)
    const filteredBooks = useFilteredBooks(sortedBooks, filter, filterType)
    return filteredBooks;
}