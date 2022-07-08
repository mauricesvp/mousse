<template>
  <div v-show="facet.data.length" class="sui-multi-checkbox-facet sui-facet">
    <div class="facet-header">
      <div class="sui-facet__title">
        {{ facet.field }}
      </div>
      <button class="sui-facet__title" v-on:click="toggleHide">Hide</button>
    </div>
    <div class="facet-hide-wrapper">
      <div v-if="facet.field === 'Degree'" class="sui-facet-search">
        <input
          class="sui-facet-search__text-input"
          type="search"
          v-on:keyup="filter"
          placeholder="Search degree.."
        >
      </div>
      <div v-if="facet.field === 'Institute'" class="sui-facet-search">
        <input
          class="sui-facet-search__text-input"
          type="search"
          v-on:keyup="filter"
          placeholder="Search institute.."
        >
      </div>
      <div v-if="facet.field === 'Group'" class="sui-facet-search">
        <input
          class="sui-facet-search__text-input"
          type="search"
          v-on:keyup="filter"
          placeholder="Search group.."
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
    // Restore pinned labels
    var valid = ["Degree", "ECTS"];
    var hideByDefault = ["Department", "Institute", "Group"];
    var facets = document.getElementsByClassName("sui-multi-checkbox-facet");
    facets.forEach(facet => {
      var facetName = facet.firstChild.firstChild.innerHTML.trim();
      if (facetName === "Exam Type") {
        // This is somewhat hacky tbh
        var facetContainer = facet.getElementsByClassName("non_facets_sticky")[0];
        var element = facetContainer.getElementsByTagName("span")[0];
        element.innerHTML = "PORTFOLIO";
      }
      if (hideByDefault.includes(facetName)) {
        var button = facet.getElementsByTagName("button")[0];
        this.toggleHideInit(button);
      }
      if (!valid.includes(facetName)) return;
      var nonSticky = facet.getElementsByClassName("non_facets_sticky")[0];
      var elements = nonSticky.getElementsByTagName("label");
      var sticky = facet.getElementsByClassName("facets_sticky")[0];
      elements.forEach(element => {
        var input = element.getElementsByTagName("input")[0];
        if (input.checked) {
          sticky.appendChild(element);
        }
      });
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
      // Filter facet with text input
      // Do not however filter pinned (selected) labels
      var ourFacet = event.currentTarget.parentElement.parentElement;

      let filter_val = event.currentTarget.value.toUpperCase();
      let wrapper = ourFacet.getElementsByClassName("non_facets_sticky")[0];
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
      function indexOf(element, list, facet) {
        // Returns index of where element should be placed within list (which is sorted)
        var tmp = Array.from(list.getElementsByClassName("sui-multi-checkbox-facet__option-label"));
        var values;
        if (facet === 'Degree') {
            values = tmp.map(e => (e.children[0].children[0].getAttribute("value")));
        } else if (facet === 'ECTS') {
            // Since the ECTS only has Numbers, we don't want to sort alphanumerically
            values = tmp.map(e => parseInt(e.children[0].children[0].getAttribute("value")));
        }
        var value = element.children[0].children[0].getAttribute("value");
        var low = 0;
        var high = values.length;
        while (low < high) {
          var mid = (low + high) >>> 1;
          if (values[mid] < value) low = mid + 1;
          else high = mid;
        }
        return low;
      }
      // Pin selected labels
      if (this.facet.field === 'Degree' || this.facet.field === 'ECTS') {
        var element = event.currentTarget.parentElement.parentElement;
        var ourFacet = element.parentElement.parentElement;
        var directParent = element.parentElement;
        var otherParent;
        if (directParent.className !== "non_facets_sticky" && !element.checked) {
          otherParent = ourFacet.getElementsByClassName("non_facets_sticky")[0];
        } else {
          otherParent = ourFacet.getElementsByClassName("facets_sticky")[0];
        }
          var index = indexOf(element, otherParent, this.facet.field);
          // Insert in the right spot
          otherParent.insertBefore(element, otherParent.childNodes[index]);
      }
    },
    toggleHide(event) {
      var button = event.currentTarget;
      var curr = button.innerHTML;
      button.innerHTML = curr === "Hide" ? "Show" : "Hide";
      button.style.fontWeight = (curr === "Hide") ? 700 : 400;
      var facetRoot = button.parentElement.parentElement;
      var facetWrapper = facetRoot.getElementsByClassName("facet-hide-wrapper")[0];
      var curr2 = facetWrapper.style.display;
      facetWrapper.style.display = curr2 === "none" ? "block" : "none";
    },
    toggleHideInit(button) {
      button.innerHTML = "Show";
      button.style.fontWeight = 700;
      var facetRoot = button.parentElement.parentElement;
      var facetWrapper = facetRoot.getElementsByClassName("facet-hide-wrapper")[0];
      facetWrapper.style.display = "none";
    }
  }
};
</script>

<style>
.sui-facet {
  margin-top: 16px !important;
}

.facet-header {
  display: flex;
  justify-content: space-between;
}

.facet-header button {
  border: none;
  background: #fff;
  outline:none;
}

.facet-header button:hover {
  cursor: pointer;
}

.sui-facet__title {
  text-transform: none !important;
}

.facet-hide-wrapper {
  display: block;
}

.facet-wrapper {
  text-overflow: ellipsis;
  word-wrap : break-word;
}
.sui-multi-checkbox-facet__option-label:hover {
  background: #eee;
}

.facets_sticky {
  position: sticky;
  background: #eee;
  /*top: 0;*/
}

.facets_sticky > :last-child {
  border-bottom: 1px solid #000;
}

.non_facets_sticky {
  max-height: 9.25rem;
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

.sui-multi-checkbox-facet__input-text {
  vertical-align: text-bottom;
}
</style>
