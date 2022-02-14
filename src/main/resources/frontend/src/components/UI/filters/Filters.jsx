import React, {useState} from 'react';
import tableClasses from "../myTable/MyTable.module.css";
import filterClasses from "./Filters.module.css";
import MyCheckbox from "../checkbox/MyCheckbox";

const Filters = ({cols, filtersData, filtersClean, filterFoo, filterClick}) => {
    const [filtersVisible, setFiltersVisible] = useState(false);
    const mainFilterCheckboxClick = () => {
        setFiltersVisible(!filtersVisible);
        filtersClean();
    }
    return (
        <div>
            <MyCheckbox value={filtersVisible} onClick={mainFilterCheckboxClick}>Фильтр</MyCheckbox>
            {filtersVisible
                ? <table className={tableClasses.foo}>
                    <thead>
                    <tr>
                        {cols.map((colName, index) =>
                            <th key={"filter_"+colName+"_"+index} className={filterClasses["filter" + (index + 1)]}>
                                {["imgUrl", "torUrl"].includes(colName)
                                    ? <div/>
                                    : <div className={filterClasses.filterThContent}>
                                        <MyCheckbox value={filtersData[colName]} onClick={() => filterClick(colName)} plusMinus={true}/>
                                        <input
                                            key={"filter" + index}
                                            style={
                                                index === 0
                                                    ? {width: "95%"}
                                                    : {width: "90%"}
                                            }
                                            onKeyUp={e => {
                                                filterFoo(colName, e.currentTarget.value);
                                            }}
                                        />
                                    </div>
                                }
                            </th>
                        )}
                    </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
                : <div/>
            }
        </div>
    );
};

export default Filters;