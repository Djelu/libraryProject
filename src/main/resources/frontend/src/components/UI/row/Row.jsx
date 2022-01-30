import React from 'react';
import ConvertingService from "../../../API/ConvertingService";
import classes from "./Row.module.css";

const Row = ({data, cols, index}) => {
    const {url, bookName, lastName, fistName} = data;
    return (
        <tr className={classes.tCenter}>
            {cols.map(colName => {
                let innerElem;
                switch (colName) {
                    case "bookName":
                        innerElem = <a href={url}>{bookName}</a>
                        break;
                    case "author":
                        innerElem = <span>{ConvertingService.getAuthor(fistName, lastName)}</span>
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