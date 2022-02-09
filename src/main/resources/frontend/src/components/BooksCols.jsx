import React from 'react';
import Col from "./UI/col/Col";

const BooksCols = ({cols, sortFoo}) => {
    return (
        <tr>
            {cols.map((colName, index) =>
                <Col key={index} colName={colName} index={index} sortFoo={sortFoo}/>
            )}
        </tr>
    );
};

export default BooksCols;