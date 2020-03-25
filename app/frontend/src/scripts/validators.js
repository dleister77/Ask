const isEmpty = (value) => value == '';

const telephone = (value) => {
  const re = /[^\d]+/g;
  const nums = value.replace(re, '');
  return nums.length == 10;
};
export { isEmpty, telephone };
