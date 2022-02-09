export default class Converting {
    static getAuthor(fistName, lastName){
        return lastName + " " + fistName;
    }
    static getGenre(genreStr){
        return genreStr.split(",").map((g, index) =>
                <span key={g + "_" + index}>{g.trim()}</span>
            );
    }
    static getValueFromBook(data, colName){
        switch (colName){
            case "author":
                const colDepends = this.getColDepends(colName)
                return this.getAuthor(data[colDepends[0]], data[colDepends[1]]);
            default:
                return data[colName];
        }
    }
    static getColDepends(colName){
        switch (colName){
            case "author":
                return ["fistName", "lastName"]
            default:
                return [colName];
        }
    }
    static getKBValue(value, type){
        switch (type.toUpperCase()){
            case "TB": return value * 1000000000;
            case "GB": return value * 1000000;
            case "MB": return value * 1000;
            default: return value;
        }
    }
}