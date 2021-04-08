<template>
  <div v-show="facet.data.length" class="sui-multi-checkbox-facet sui-facet">
    <div class="sui-facet__title">
      {{ facet.field }}
    </div>
    <div v-if="facet.field === 'Degree'" class="sui-facet-search">
      <input
        class="sui-facet-search__text-input"
        type="search"
        v-on:keyup="filter"
        placeholder="Search degree.."
      >
    </div>
    <div class="facet-wrapper">
      <div class="sui-multi-checkbox-facet__option-input-wrapper">
        <div class="facets_sticky">
        </div>
        <div class="non_facets_sticky">
            <label
              v-for="facetItem in facet.data"
              :key="facetItem.value"
              class="sui-multi-checkbox-facet__option-label"
            >
              <div class="sui-multi-checkbox-facet__option-input-wrapper">
                <input
                  class="sui-multi-checkbox-facet__checkbox"
                  type="checkbox"
                  :value="getValue(facetItem, facet.type)"
                  :checked="isChecked(getValue(facetItem, facet.type))"
                  @change="$emit('change', $event); handleSticky($event)"
                />
                <span class="sui-multi-checkbox-facet__input-text">{{
                  getValue(facetItem, facet.type)
                }}</span>
              </div>
              <span class="sui-multi-checkbox-facet__option-count">{{
                facetItem.count
              }}</span>
            </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    facet: {
      type: Object,
      required: true
    },
    checked: {
      type: Array,
      required: true
    }
  },
  mounted() {
    var nonSticky = document.getElementsByClassName("non_facets_sticky")[0];
    var elements = nonSticky.getElementsByTagName("label");
    var sticky = document.getElementsByClassName("facets_sticky")[0];
    elements.forEach(element => {
      var input = element.getElementsByTagName("input")[0];
      if (input.checked) {
        sticky.appendChild(element);
      }
    });
  },
  methods: {
    isChecked(value) {
      return this.checked && this.checked.includes(value);
    },
    getValue(facetItem, type) {
      return type === "range" ? facetItem.value.name : facetItem.value;
    },
    filter(event) {
      // Filter degrees with text input
      // Do not however filter pinned (selected) degrees
      let filter_val = event.currentTarget.value.toUpperCase();
      let wrapper = document.getElementsByClassName("non_facets_sticky")[0];
      let elements = wrapper.getElementsByClassName("sui-multi-checkbox-facet__option-label");
      var i;
      for (i = 0; i < elements.length; i++) {
        var element = elements[i];
        var span = element.getElementsByTagName("span")[0];
        var textValue = span.innerHTML.toUpperCase();
        if (textValue.indexOf(filter_val) > -1 ) {
          element.style.display = "";
        } else {
          element.style.display = "none";
        }
      }
    },
    handleSticky(event) {
      // Pin selected degrees
      if (this.facet.field === 'Degree') {
        var element = event.currentTarget.parentElement.parentElement;
        var directParent = element.parentElement;
        var otherParent;
        if (directParent.className !== "non_facets_sticky" && !element.checked) {
          otherParent = document.getElementsByClassName("non_facets_sticky")[0];
        } else {
          otherParent = document.getElementsByClassName("facets_sticky")[0];
        }
        otherParent.appendChild(element);
      }
    }
  }
};
</script>

<style>
.sui-facet {
  margin-top: 16px !important;
}

.facet-wrapper {
  text-overflow: ellipsis;
  word-wrap : break-word;
}

.facets_sticky {
  position: sticky;
  background: #eee;
  top: 0;
}

.facets_sticky > :last-child {
  border-bottom: 1px solid #000;
}

.non_facets_sticky {
  max-height: 12rem;
  overflow-y: auto;
  overflow-x: hidden;
}

@media only screen and (max-width: 767px) {
  .non_facets_sticky {
    max-height: 8rem;
  }
}

.sui-facet-search {
  padding: 0.5rem 0;
  margin: 0 !important;
}

.sui-multi-checkbox-facet__option-count {
  padding-right: 0.5rem;
}
</style>
