import React from 'react';
import ConvertingService from "../../../API/ConvertingService";
import classes from "./Row.module.css";

const Row = ({data, cols, index, itemClassName}) => {
    const {url, bookName} = data;
    return (cols.map(colName => {
        let innerElem;
        switch (colName) {
            case "bookName":
                innerElem = <a href={url}>{bookName}</a>
                break;
            case "author":
                innerElem = <span>{ConvertingService.getValueFromBook(data, colName)}</span>
                break;
            case "genre":
                innerElem = <div className={classes.inColumn}>
                    {ConvertingService.getGenre(data[colName])}
                </div>
                break;
            case "imgUrl":
                innerElem = <img src={data[colName]} alt="pic" width="200" height="200"/>
                break;
            case "torUrl":
                innerElem =
                    // <a href={"https://rutracker.org/forum/dl.php?t="+data["bookPageId"]}>
                    //     <img src="https://static.t-ru.org/templates/v1/images/attach_big.gif"
                    //          alt="Скачать .torrent"/><br/>
                    //     Скачать .torrent
                    // </a>
                    <a href={"https://rutracker.org/forum/dl.php?t="+data["bookPageId"]}>
                        <img src="https://static.t-ru.org/templates/v1/images/attach_big.gif" alt="Скачать .torrent"/>
                    </a>
                break;
            default:
                innerElem = <span>{data[colName]}</span>
        }
        return <div key={colName+"_"+index} className={itemClassName}>{innerElem}</div>;
    }));
};

export default Row;