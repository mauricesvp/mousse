<template>
  <ul class="sui-results-container search-section__search-results">
    <li
      v-for="result in results"
      :key="result.id"
      class="search-result"
    >
      <SearchResult :result="result" />
    </li>
  </ul>
</template>

<script>
import SearchResult from "./SearchResult";

export default {
  components: {
    SearchResult
  },
  props: {
    results: {
      type: Array,
      required: true
    }
  },
  methods: {
    sort(event) {
      this.$emit('input', event.target.id);
    }
  }
};
</script>

<style scoped>
.search-section__search-results {
  display: flex;
  flex-direction: column;
  list-style: none;
  background: white;
  width: 100%;
}

.search-result {
  display: flex;
}

li:nth-child(odd) {
  background: #ddd;
}

.clickable:hover {
  cursor: pointer;
}
</style>
