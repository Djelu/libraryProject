import React, {useState} from 'react';
import Row from "./UI/row/Row";
import classes from "./UI/myTable/MyTable.module.css";

const BooksRows = ({books, cols}) => {
    const [openedRow, setOpenedRow] = useState(-1);
    return (
        books.map((data, index) =>
            <Row key={data["bookPageId"]} data={data} cols={cols} rowIndex={index}
                 setOpenedRow={setOpenedRow}
                 rowOpened={openedRow===index}
                 itemClassName={classes.item + " " + (classes["item"+(index+1)])}/>
         )
    );
};

export default BooksRows;