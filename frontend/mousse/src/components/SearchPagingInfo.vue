<template>
  <div class="sui-paging-info">
    Showing
    <strong>{{ start }} - {{ Math.min(end, searchState.totalResults) }}</strong>
    out of <strong>{{ searchState.totalResults }}</strong>
    <template v-if="searchState.searchTerm">
        for:
        <em>"{{ searchState.searchTerm }}"</em>
    </template>
  </div>
</template>

<script>
export default {
  props: {
    searchState: {
      required: true,
      type: Object
    }
  },
  computed: {
    start() {
      return this.searchState.totalResults === 0
        ? 0
        : (this.searchState.current - 1) * this.searchState.resultsPerPage + 1;
    },
    end() {
      return this.searchState.totalResults <= this.searchState.resultsPerPage
        ? this.searchState.totalResults
        : this.start + this.searchState.resultsPerPage - 1;
    }
  }
};
</script>
