import React, {useState} from 'react';
import classes from "./Col.module.css";

const Col = ({colName, sortFoo}) => {
    let innerText;
    switch (colName) {
        case "bookName": innerText = "Название"; break;
        case "author": innerText = "Автор"; break;
        case "genre": innerText = "Жанры"; break;
        case "year": innerText = "Год"; break;
        case "bookDuration": innerText = "Длина"; break;
    }

    const [isUp, setIsUp] = useState(null);

    return (
        <th>
            <div onClick={() => {
                const newIsUp = !isUp;
                setIsUp(newIsUp)
                sortFoo(colName, newIsUp);
            }}>
                <span>{innerText}</span>
                <span>{isUp==null ?"" :(isUp?"↑" :"↓")}</span>
            </div>
        </th>
    );
};

export default Col;