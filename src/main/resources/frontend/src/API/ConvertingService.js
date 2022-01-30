export default class Converting {
    static getAuthor(fistName, lastName){
        return lastName + " " + fistName;
    }
    static getGenre(genreStr){
        return genreStr.split(",").map((g, index) =>
                <span key={g + "_" + index}>{g.trim()}</span>
            );
    }
    static getColDepends(name){
        switch (name){
            case "author":
                return ["fistName", "lastName"]
            default:
                return [name];
        }
    }
}