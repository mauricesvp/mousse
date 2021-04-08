<template>
  <div class="sui-results-per-page">
    <div class="sui-results-per-page__label">Show</div>
        <select
          name="resultsPerPage"
          :value="value"
          @input="$emit('input', $event.target.value)"
          class="sui-select sui-select--inline"
        >
          <option :value="20">20</option>
          <option :value="50">50</option>
          <option :value="100">100</option>
        </select>
    </div>
</template>

<script>
export default {
  props: {
    value: {
      type: Number,
      required: true
    }
  }
};
</script>
