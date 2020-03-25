const paginationNav = {
  props: {
    pagination_urls: {
      type: Object,
      required: true,
    },
    pages: {
      type: Array,
      required: true,
    },
  },
  template: `
  <nav aria-label="Page navigation">
      <ul class="pagination">
          <li
            v-if="pagination_urls.prev"
            class="page-item">
            <a
              class="page-link"
              v-bind:href="pagination_urls.prev">
              Previous
              </a>
          </li>

          <li 
            class="page-item"
            v-for="page in pages"
            v-bind:key="page[0]">
            <a
              class="page-link"
              v-bind:href="page[1]">
              {{page[0]}}
            </a>
          </li>

          <li
            v-if="pagination_urls.next"
            class="page-item">
            <a
              class="page-link"
              v-bind:href="pagination_urls.next">
              Next
            </a>
          </li>
      </ul>
  </nav>            
  `,
};

export default paginationNav;
