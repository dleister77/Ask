/* eslint-disable no-param-reassign */
import axios from 'axios';
import { len } from 'vuelidate/lib/validators/common';

const categoryGetUrl = '/categorylist';
const sectorGetUrl = '/sectorlist';

function updateSelectFieldOptions(response, id) {
  const selectField = document.getElementById(id);
  // remove existing options
  while (selectField.hasChildNodes()) {
    selectField.removeChild(selectField.firstChild);
  }
  Array.from(response.data).forEach((item) => {
    const option = document.createElement('option');
    option.textContent = item.name;
    option.value = item.id;
    selectField.appendChild(option);
  });
}

function categoryGet(url, sector, categoryId) {
  axios.get(url, {
    params: {
      sector,
    },
  })
    .then((response) => updateSelectFieldOptions(response, categoryId))
    .catch((error) => console.log(error));
}

async function getCategoryList(sector = null) {
  try {
    const response = await axios.get(categoryGetUrl, {
      params: {
        sector,
      },
    });
    return response.data;
  } catch (error) {
    console.log(`error: ${error}`);
    return null;
  }
}

async function getSectorList() {
  try {
    const response = await axios.get(sectorGetUrl);
    return response.data;
  } catch (error) {
    console.log(error);
    return null;
  }
}

function makeForm(object) {
  const form = new FormData();
  Object.entries(object).forEach(([k, v]) => form.set(k, v));
  return form;
}

function postForm(path, params, method = 'post') {
  const form = document.createElement('form');
  form.method = method;
  form.action = path;

  Object.keys(params).forEach((key) => {
    const hiddenField = document.createElement('input');
    hiddenField.type = 'hidden';
    hiddenField.name = key;
    hiddenField.value = params[key];
    form.append(hiddenField);
  });
  // for (const key in params) {
  //   if (params.hasOwnProperty(key)) {
  //     const hidden_field = document.createElement('input');
  //     hidden_field.type = "hidden";
  //     hidden_field.name = key;
  //     hidden_field.value = params[key];

  //     form.append(hidden_field);
  //   }
  // }
  document.body.appendChild(form);
  form.submit();
}

function resetForm(formOld) {
  const formNew = {};
  Object.entries(formOld).forEach(([key, value]) => {
    switch (typeof value) {
      case 'string':
        formNew[key] = '';
        break;
      case 'boolean':
        formNew[key] = false;
        break;
      case 'number':
        formNew[key] = 0;
        break;
      case 'undefined':
        formNew[key] = null;
        break;
      default:
        if (value instanceof Array) {
          formNew[key] = Array(0);
        } else if (value == null) {
          formNew[key] = null;
        } else if (len(Object.keys(value)) > 0) {
          formNew[key] = resetForm(value);
        } else {
          formNew[key] = null;
        }
        break;
    }
  });
  return formNew;
}

function isObjectLiteral(value) {
  if (typeof value !== 'object' || value instanceof Array || value == null) {
    return false;
  } if (len(Object.keys(value)) > 0) {
    return true;
  } return false;
}

function setForm(formPresets, form) {
  Object.entries(formPresets).forEach(([key, value]) => {
    if (isObjectLiteral(value)) {
      form[key] = setForm(value, form[key]);
    } else {
      form[key] = value;
    }
  });
  return form;
}

export {
  categoryGet, getCategoryList, getSectorList, makeForm, postForm,
  resetForm, setForm,
};
