import React from 'react';
import Row from "./UI/row/Row";
import classes from "./UI/myTable/MyTable.module.css";

const BooksRows = ({books, cols}) => {
    return (
        books.map((data, index) =>
            <Row key={data["bookPageId"]} data={data} cols={cols} index={index}
                 itemClassName={classes.item + " " + (classes["item"+(index+1)])}/>
         )
    );
};

export default BooksRows;