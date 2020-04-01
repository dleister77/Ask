const NavListButton = {
  props: {
    eventSignal: {
      type: String,
      required: true,
    },
  },
  inheritAttrs: false,
  template: `
        <li class="nav-item">
            <button
                ref="b"
                type="button"
                class="btn btn-link nav-link"
                v-bind="$attrs"
                v-on:click="$emit(eventSignal)">
            <slot></slot>
            </button>
        </li>
    `,
};

export default NavListButton;
