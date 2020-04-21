import { VBTooltip } from 'bootstrap-vue';

const NavListButton = {
  directives: {
    'b-tooltip': VBTooltip,
  },
  props: {
    disabled: {
      type: Boolean,
      required: false,
    },
    eventSignal: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: false,
    },
    tooltipTitle: {
      type: String,
      required: false,
    },
  },
  inheritAttrs: false,
  template: `
        <li class="nav-item align-self-center">
            <button
                ref="b"
                type="button"
                class="btn btn-link nav-link py-0"
                :disabled="disabled"
                v-bind="$attrs"
                v-b-tooltip = "{ title: tooltipTitle, disabled: $root.isMobile }"
                @click="$emit(eventSignal)">
            <slot></slot>
            </button>
            <small
              class="d-block d-md-none text-center"
            > {{ title }} </small>
        </li>
    `,
};

export default NavListButton;
