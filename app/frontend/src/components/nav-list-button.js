
const NavListButton = {
  props: {
    eventSignal: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: false,
    }
  },
  inheritAttrs: false,
  template: `
        <li class="nav-item align-self-center">
            <button
                ref="b"
                type="button"
                class="btn btn-link nav-link py-0"
                v-bind="$attrs"
                v-on:click="$emit(eventSignal)">
            <slot></slot>
            </button>
            <small class="d-block d-md-none text-center"> {{ title }} </small>
        </li>
    `,
};

export default NavListButton;
