import React from 'react';
import classes from "./SpecMsg.module.css";

const SpecMsg = ({children}) => {
    return (
        <tr>
            <td>
                <div className={classes.cCenter}>
                    {children}
                </div>
            </td>
        </tr>
    );
};

export default SpecMsg;