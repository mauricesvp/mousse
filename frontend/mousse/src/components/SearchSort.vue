<template>
  <div class="sui-sorting">
    <div class="sui-sorting__label">Sort:</div>
    <select
      name="sortBy"
      @input="$emit('input', $event.target.value)"
    >
      <option value="" disabled selected>Select</option>
      <option value="name_strAsc">A-Z</option>
      <option value="name_str">Z-A</option>
      <option value="ects_iAsc">ECTS asc.</option>
      <option value="ects_i">ECTS desc.</option>
    </select>
  </div>
</template>

<script>
export default {
  props: {
    value: {
      type: String,
      required: true
    }
  }
};
</script>
