import React from 'react';
import colClasses from "./Filter.module.css";

const Filter = ({cols, filterFoo}) => {
    return (
        <div style={{display: "flex"}}>
            {cols.map((colName, index) =>
                ["imgUrl", "torUrl"].includes(colName)
                ? <div key={"filter" + index} className={colClasses["filter" + (index + 1)]}/>
                : <input
                        key={"filter" + index}
                        className={colClasses["filter" + (index + 1)]}
                        onKeyUp={e => {
                            filterFoo(colName, e.currentTarget.value);
                        }}
                />
            )}
        </div>
    );
};

export default Filter;