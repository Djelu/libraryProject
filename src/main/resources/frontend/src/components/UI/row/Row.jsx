import React from 'react';
import ConvertingService from "../../../API/ConvertingService";
import classes from "./Row.module.css";

const Row = ({data, cols, index}) => {
    const {url, book_name, last_name, fist_name} = data;
    return (
        <tr className={classes.tCenter}>
            {cols.map(colName => {
                let innerElem;
                switch (colName) {
                    case "book_name":
                        innerElem = <a href={url}>{book_name}</a>
                        break;
                    case "author":
                        innerElem = <span>{ConvertingService.getAuthor(fist_name, last_name)}</span>
                        break;
                    case "genre":
                        innerElem = <div className={classes.inColumn}>
                            {ConvertingService.getGenre(data[colName])}
                        </div>
                        break;
                    default:
                        innerElem = <span>{data[colName]}</span>
                }
                return <td key={colName + "_" + index} className={classes.tLeft}>{innerElem}</td>
            })}
        </tr>
    );
};

export default Row;