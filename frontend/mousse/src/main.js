import Vue from 'vue'
import App from './App.vue'

import {
  enable as enableDarkMode,
  setFetchMethod,
} from 'darkreader';

setFetchMethod(window.fetch);

enableDarkMode({
  brightness: 100,
  contrast: 90,
  sepia: 10,
});

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')
