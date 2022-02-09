import React from 'react';
import Loader from "./UI/loader/Loader";
import SpecMsg from "./UI/specMsg/SpecMsg";

const HandledElem = ({children, error, isLoading}) => {
    if (!error && !isLoading)
        return (children)
    return (
        <SpecMsg> {
            error
                ? <div/>
                : <Loader/>
        }</SpecMsg>
    );
};

export default HandledElem;