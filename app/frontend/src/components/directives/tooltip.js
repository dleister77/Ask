import Vue from 'vue';

const tooltip = {
  bind: async (el, binding) => {
    await Vue.nextTick();
    $(el).tooltip({
      title: binding.value,
      placement: binding.arg,
      trigger: 'hover',
    });
  },
  update: async (el, binding) => {
    $(el).tooltip('dispose');
    $(el).tooltip({
      title: binding.value,
      placement: binding.arg,
      trigger: 'hover',
    });
  },
  unbind: (el, binding) => {
    $(el).tooltip('dispose');
  },
}

export default tooltip;