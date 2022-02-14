export default class Converting {
    static getObjWithDefaultValues(keys, defVal){
        let result = {};
        keys.forEach(key => result[key] = defVal)
        return result
    }
}