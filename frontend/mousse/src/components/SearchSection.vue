<template>
  <div class="sui-layout">
    <SearchHeader v-model="searchInputValue" @submit="handleFormSubmit" />
    <div v-if="searchState.wasSearched" class="sui-layout-body">
      <div class="sui-layout-body__inner">
        <div class="sui-layout-sidebar--toggled">
          <SearchSort v-show="thereAreResults" v-model="sortBy" />

          <SearchFacet
            :checked="degrees"
            v-if="searchState.facets.degrees"
            :facet="searchState.facets.degrees[0]"
            @change="handleFacetChange($event, 'degrees')"
          />

          <SearchFacet
            :checked="cycles"
            v-if="searchState.facets.cycles"
            :facet="searchState.facets.cycles[0]"
            @change="handleFacetChange($event, 'cycles')"
          />

          <SearchFacet
            :checked="types"
            v-if="searchState.facets.types"
            :facet="searchState.facets.types[0]"
            @change="handleFacetChange($event, 'types')"
          />

          <SearchFacet
            :checked="ects"
            v-if="searchState.facets.ects"
            :facet="searchState.facets.ects[0]"
            @change="handleFacetChange($event, 'ects')"
          />

          <SearchFacet
            :checked="examtypes"
            v-if="searchState.facets.examtypes"
            :facet="searchState.facets.examtypes[0]"
            @change="handleFacetChange($event, 'examtypes')"
          />

          <SearchFacet
            :checked="departments"
            v-if="searchState.facets.departments"
            :facet="searchState.facets.departments[0]"
            @change="handleFacetChange($event, 'departments')"
          />
        </div>
        <div class="sui-layout-main">
          <div class="sui-layout-main-header">
            <div class="sui-layout-main-header__inner">
              <SearchPagingInfo :search-state="searchState" />
              <SearchResultsPerPage
                v-show="thereAreResults"
                v-model.number="resultsPerPage"
              />
            </div>
          </div>
          <div class="sui-layout-main-body">
            <SearchResults
              v-show="thereAreResults"
              :results="searchState.results"
              v-model="sortBy"
            />
          </div>
          <div class="sui-layout-main-footer">
            <SearchPagination
              v-show="thereAreResults"
              :total-pages="Math.min(searchState.totalPages, 100)"
              :click-handler="setCurrentPage"
            />
          </div>
        </div>
      </div>
    </div>
    <div class="quick_links">
      <a href="https://freitagsrunde.org/">Freitagsrunde</a>
      <a href="https://github.com/mauricesvp/mousse">Source</a>
      <a href="https://tu.berlin">TU Berlin</a>
      <a href="https://moseskonto.tu-berlin.de/moses/modultransfersystem/index.html">MTS</a>
    </div>
  </div>
</template>

<script>
import { SearchDriver } from "@elastic/search-ui";
import config from "../searchConfig";
import SearchResults from "./SearchResults";
import SearchFacet from "./SearchFacet";
import SearchHeader from "./SearchHeader";
import SearchPagingInfo from "./SearchPagingInfo";
import SearchPagination from "./SearchPagination";
import SearchSort from "./SearchSort";
import SearchResultsPerPage from "./SearchResultsPerPage";

const driver = new SearchDriver(config);

export default {
  components: {
    SearchResults,
    SearchFacet,
    SearchHeader,
    SearchPagingInfo,
    SearchPagination,
    SearchSort,
    SearchResultsPerPage
  },
  data() {
    return {
      searchInputValue: "",
      searchState: {},
      cycles: [],
      types: [],
      ects: [],
      degrees: [],
      departments: [],
      examtypes: [],
      resultsPerPage: 20,
      sortBy: "name"
    };
  },
  computed: {
    thereAreResults() {
      return this.searchState.totalResults && this.searchState.totalResults > 0;
    }
  },
  watch: {
    resultsPerPage(newResultsPerPage) {
      if (newResultsPerPage > 100) newResultsPerPage = 100;
      driver.setResultsPerPage(newResultsPerPage);
    },
    sortBy(newSortBy) {
      if (newSortBy.endsWith("Asc")) {
        driver.setSort(newSortBy.replace("Asc", ""), "asc");
      } else {
        driver.setSort(newSortBy, "desc");
      }
    }
  },
  mounted() {
    const {
      searchTerm,
      sortField,
      resultsPerPage,
      filters
    } = driver.getState();

    // restoring UI from url query
    this.searchInputValue = searchTerm;
    this.sortBy = sortField;
    this.resultsPerPage = resultsPerPage;
    filters.forEach(filter => {
      if (filter.field === "price") { // Use this for range facets
        this[filter.field] = filter.values.map(value => value.name);
      } else {
        this[filter.field] = filter.values;
      }
    });

    driver.subscribeToStateChanges(state => {
      this.searchState = state;
    });
  },
  methods: {
    handleFormSubmit() {
      driver.getActions().setSearchTerm(this.searchInputValue);
    },
    handleFacetChange(event, facet) {

      const { value, checked } = event.target;
      const facetFromDriver = driver.getState().facets[facet][0];
      const valueforApi =
        facetFromDriver.type === "range"
          ? facetFromDriver.data.find(item => item.value.name === value).value
          : value;

      if (checked) {
        this[facet].push(value);
        driver.addFilter(facet, valueforApi, "any");
      } else {
        const index = this[facet].indexOf(value);
        if (index > -1) {
          this[facet].splice(index, 1);
        }
        driver.removeFilter(facet, valueforApi, "any");
      }
    },
    setCurrentPage(page) {
      driver.setCurrent(page);
    }
  }
};
</script>

<style>
.sui-layout-main {
  width: auto !important;
  min-width: 70%;
}

.quick_links {
  max-width: 1300px;
  width: 100%;
  margin: 0 auto;
  text-align: center;
  border-top: 2px solid #336;
  padding: 1rem 0 2rem 0;
}

.quick_links > a + a {
  border-left: 2px solid #336;
}

.quick_links a {
  padding: 0 0.5rem;
  font-size: 1.25rem;
  text-decoration: none;
  color: #222;
  transition-duration: 0.4s;
}

.quick_links a:hover {
  font-size: 1.3rem;
  text-shadow: 2px 2px 4px #aaa;
}

.sui-layout-sidebar--toggled {
  min-width: 30%;
}
</style>
