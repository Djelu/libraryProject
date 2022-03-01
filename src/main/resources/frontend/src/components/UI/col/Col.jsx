import React, {useState} from 'react';
import classes from "./Col.module.css";

const Col = ({colName, sortFoo, itemClassName}) => {
    let innerText;
    let onClickFoo;
    let sortDirection;

    switch (colName) {
        case "bookName": innerText = "Название"; break;
        case "author": innerText = "Автор"; break;
        case "genre": innerText = "Жанры"; break;
        case "year": innerText = "Год"; break;
        case "bookDuration": innerText = "Длина"; break;
        case "imgUrl": innerText = "Картинка"; break;
        case "torUrl": innerText = "Торрент"; break;
        case "torSize": innerText = "Размер"; break;
    }

    const [isUp, setIsUp] = useState(null);

    if (["imgUrl", "torUrl"].includes(colName)) {
        sortDirection = ""
    } else {
        sortDirection = isUp == null ? "" : (isUp ? "↑" : "↓")
        const getNewDirection = function (oldDirectionIsUp){//isUp
            switch (oldDirectionIsUp) {
                case true: return false;
                case false: return null;
                default: return true;
            }
        }
        onClickFoo = function () {
            const newIsUp = getNewDirection(isUp);
            setIsUp(newIsUp)
            sortFoo(colName, newIsUp);
        }

    }

    return (
        <div onClick={onClickFoo} className={itemClassName}>
            <span>{innerText}</span>
            <span>{sortDirection}</span>
        </div>
    );
};

export default Col;