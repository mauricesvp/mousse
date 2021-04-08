<template>
  <div class="sui-layout-header">
    <div class="sui-search-box__wrapper">
      <form @submit.prevent="$emit('submit', $event.target.value)">
        <div class="sui-search-box">
            <input
              type="text"
              placeholder="Search this, search that ..."
              class="sui-search-box__text-input"
              :value="value"
              @input="$emit('input', $event.target.value)"
            />
          <input
            type="submit"
            class="button sui-search-box__submit"
            value="Search"
          />
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    value: {
      required: true,
      type: String
    }
  }
};
</script>

<style scoped>
.sui-layout-header {
  padding-top: 1rem;
  display: flex;
}

.sui-search-box__wrapper {
  display: inline-block;
  max-width: 700px;
  min-width: 10rem;
  margin-top: 0;
  margin-left: auto;
  margin-right: auto;
}

.header-text {
  display: inline-block;
  vertical-align: middle;
  margin-right: 1rem;
}

.header-text a {
  font-size: 3rem;
  font-style: italic;
  font-weight: 600;
  color: #000;
  text-decoration: none;
}
</style>
