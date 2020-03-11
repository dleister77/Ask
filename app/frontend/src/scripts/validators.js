const isEmpty = (value) => value == "";

const telephone = function(value){
    let re = /[^\d]+/g
    let nums = value.replace(re, "")
    let length = nums.length
    return length == 10
}
export {isEmpty, telephone};

