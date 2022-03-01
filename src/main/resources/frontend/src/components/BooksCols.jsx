import React from 'react';
import Col from "./UI/col/Col";
import classes from "./UI/myTable/MyTable.module.css";

const BooksCols = ({cols, sortFoo}) => {
    return (
        cols.map((colName, index) =>
            <Col key={index} colName={colName} sortFoo={sortFoo}
                 itemClassName={classes.item + " " + (classes["item"+(index+1)])}/>
        )
    );
};

export default BooksCols;