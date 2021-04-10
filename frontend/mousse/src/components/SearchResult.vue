<template>
  <div class="search-result">
    <div class="module_title">
      <div class="grow_col module_name">
        <a :href="url">{{ result["name"][0] }}</a>
      </div>
      <div class="module_info module_header">
        <p>({{ result['language'][0] }}/</p>
        <p>{{ result['ects'][0] }} LP)</p>
      </div>
      <div class="fixed_col module_header">
        <p>Type</p>
      </div>
      <div class="fixed_col module_header">
        <p>Cycle</p>
      </div>
    </div>
    <div
      v-for="(item, index) in result['parts.cycle']"
      :key="item.name_part"
      class="module_part"
    >
      <div class="grow_col">
        <p>• {{ result['parts.name_part'][index] }}</p>
      </div>
      <div class="fixed_col">
        <p>{{ result['parts.type'][index] }}</p>
      </div>
      <div class="fixed_col">
        <p>{{ item }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      url: "",
    }
  },
  props: {
    result: {
      type: Object,
      required: true
    }
  },
  mounted: function() {
    this.url =
    `https://moseskonto.tu-berlin.de/moses/modultransfersystem/bolognamodule/beschreibung/anzeigen.html?number=${this.result.id}&version=${this.result.version}`;
  },
};
</script>

<style scoped>
.search-result {
  display: flex;
  flex-wrap: wrap;
  flex-direction: column;
  width: 100%;
  border: 1px solid #f0f0f0;
}

.module_title {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  border-bottom: 1px solid #bbb;
  padding: 0.25rem 0;
}

.module_name a {
  text-decoration: none;
  -webkit-box-decoration-break: clone;
  box-decoration-break: clone;
  font-weight: 800;
  color: #000;
  font-size: 1.25rem;
  padding-left: 0.25rem;
}

.module_name a:hover {
  color: #444;
}

.module_header p {
  font-weight: 600;
}

.module_info {
  white-space: nowrap;
  text-align: center;
}

.module_part {
  display: flex;
  justify-content: flex-end;
  padding: 0.25rem 0;
  padding-left: 0.25rem;
  -webkit-box-decoration-break: clone;
  box-decoration-break: clone;
}

.module_part + .module_part {
  border-top: 1px solid #bbb;
}

p {
  display: inline;
}

.grow_col {
  flex-grow: 1;
}

.fixed_col {
  flex-shrink: 0;
  width: 5rem;
  text-align: center;
}

/* Medium sized screens */
@media only screen and (max-width: 1000px) {
  p {
    font-size: 0.875rem;
  }

  .module_name a {
    font-size: 1rem;
  }

  .module_info {
    font-size: 0.75rem;
  }

  .fixed_col {
    width: 4rem;
  }
}

/* Small screens */
@media only screen and (max-width: 767px) {
  p {
    font-size: 0.75rem;
  }

  .module_name a {
    font-size: 0.875rem;
  }

  .module_info {
    display: none;
  }

  .module_part {
    padding: 0.125rem 0;
    padding-left: 0.25rem;
  }

  .fixed_col {
    width: 3rem;
  }
}

/* Very small screens */
@media only screen and (max-width: 576px) {
  p {
    font-size: 0.675rem;
  }

  .module_name a {
    font-size: 0.75rem;
  }
}
</style>
