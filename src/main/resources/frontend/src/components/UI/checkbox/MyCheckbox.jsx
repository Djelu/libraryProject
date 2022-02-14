import React from 'react';
import classes from './MyCheckbox.module.css'

const MyCheckbox = ({value, onClick, children, plusMinus=false}) => {
    return (
        plusMinus
            ? <div className={classes.plusMinus} onClick={onClick}>
                {value
                    ? "+"
                    : "-"}
            </div>
            : <div>
                <input type="checkbox" checked={value} onClick={onClick}/>
                <label>{children}</label>
            </div>
    );
};

export default MyCheckbox;