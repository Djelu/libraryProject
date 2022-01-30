export default class Converting {
    static getAuthor(fist_name, last_name){
        return last_name + " " + fist_name;
    }
    static getGenre(genreStr){
        return genreStr.split(",").map((g, index) =>
                <span key={g + "_" + index}>{g.trim()}</span>
            );
    }
    static getColDepends(name){
        switch (name){
            case "author":
                return ["fist_name", "last_name"]
            default:
                return [name];
        }
    }
}