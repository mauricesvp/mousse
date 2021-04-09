<template>
  <div id="app">
    <SearchSection />
  </div>
</template>

<script>
import SearchSection from './components/SearchSection.vue'

export default {
  name: 'App',
  components: {
    SearchSection
  }
}
</script>

<style>
@import "../node_modules/@elastic/react-search-ui-views/lib/styles/styles.css";
@import url('https://fonts.googleapis.com/css2?family=Lato&display=swap');

html {
  margin-left: calc(100vw - 100%);
  margin-right: 0;
}

body {
  padding: 0;
  margin: 0 auto;
}

#app {
  /*font-family: Avenir, Helvetica, Arial, sans-serif;*/
  font-family: 'Lato', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-size: 16px;
  color: #2c3e50;
}
</style>
