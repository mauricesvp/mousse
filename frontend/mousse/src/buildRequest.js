import facets from './facets.js';

/*
 * Solr expects "start" and "rows"
 */

function buildStart(current, resultsPerPage) {
  if (!current || !resultsPerPage) return;
  return (current - 1) * resultsPerPage;
}

function buildSort(sortDirection, sortField) {
  if (sortDirection && sortField) {
    // Sanitazation?
    return `${sortField} ${sortDirection}`;
  } else return "name_str asc";
}

function buildMatch(searchTerm) {
  return searchTerm
    ? {
        multi_match: {
          query: searchTerm,
          fields: ["title", "description"]
        }
      }
    : { match_all: {} };
}

function buildFilterQuery(filters) {
    let fq = "";
    filters.forEach(filter => {
        if (filter.field == "price") {
            fq += "&fq=";
            filter.values.forEach(range => {
                // Note that "price" is hardcoded for now
                fq += "+price:[" + (range.from ? range.from : "*") + " TO " + (range.to ? range.to : "*") + "] ";
            });
        } else {
            fq += "&fq=";
            let field = "";
            switch(filter.field) {
                case "cycles":
                    field = "parts.cycle";
                    break;
                case "types":
                    field = "parts.type";
                    break;
                case "ects":
                    field = "ects";
                    break;
                case "degrees":
                    field = "degrees.name_degree";
                    break;
            }
            filter.values.forEach(value => {
                if (field === "degrees.name_degree") {
                    value = "\"" + value + "\"";
                }
                fq += "+" + field + ":" + value;
            });
        }
    });
    return fq;
}
export default function buildRequest(state) {
  const {
    current,  // Page offset
    filters,
    resultsPerPage,
    searchTerm,
    sortDirection,  // asc or desc
    sortField
  } = state;


  const sort = buildSort(sortDirection, sortField);
  const match = buildMatch(searchTerm);
  const start = buildStart(current, resultsPerPage);
  const filter = buildFilterQuery(filters);

  sort;
  match;
  var query;
  if (searchTerm !== "") {
      // Remove any non-alphanumeric char (excluding whitespace)
      var term = searchTerm.replace(/[^0-9a-z ]/gi, '');
      var splits = term.split(" ");
      query = "(*" + splits.join("* AND *") + "*)";
  }
  const body = {
      "q": (query) ? "name:" + query : "*:*",
      "start": start,
      "rows": resultsPerPage,
      "sort": sort,
  };

  return {
      body: body,
      facets: facets,
      filters: filter,
  };
}
