String.prototype.capitalize = function() {
        return this.charAt(0).toUpperCase() + this.slice(1);
}

function getValueFacet(aggregations, fieldName) {
  if (
    aggregations &&
    aggregations[fieldName] &&
    aggregations[fieldName].buckets &&
    aggregations[fieldName].buckets.length > 0
  ) {
    return [
      {
        field: fieldName,
        type: "value",
        data: aggregations[fieldName].buckets.map(bucket => ({
          value: bucket.val.toString().toUpperCase(),
          count: bucket.count
        }))
      }
    ];
  }
}

/* We are not using any range facets
function getRangeFacet(aggregations, fieldName) {
  if (
    aggregations &&
    aggregations[fieldName] &&
    aggregations[fieldName].buckets &&
    aggregations[fieldName].buckets.length > 0
  ) {
    // This is not very clean
    const buckets = aggregations[fieldName].buckets;
    const step = buckets[1].val - buckets[0].val;
    const lastFrom = buckets[buckets.length -1].val+step;
    const lastCount = aggregations[fieldName].after.count;
    const data = aggregations[fieldName].buckets.map(bucket => ({
          value: {
            to: bucket.val + step,
            from: bucket.val,
            name: (bucket.val).toString() + "-" + (bucket.val+step).toString() + " €"
          },
          count: bucket.count
        }))
    data.push({
      value: {
        to: null,
        from: lastFrom,
        name: (lastFrom).toString() + "+ €"
      },
        count: lastCount
    })
    return [
      {
        field: fieldName,
        type: "range",
        data: data
      }
    ];
  }
}
*/

export default function buildStateFacets(aggregations) {
  const cycles = getValueFacet(aggregations, "Cycle");
  const types = getValueFacet(aggregations, "Type");
  const ects = getValueFacet(aggregations, "ECTS");
  const degrees = getValueFacet(aggregations, "Degree");

  const facets = {
    ...(cycles && { cycles }),
    ...(types && { types }),
    ...(ects && { ects }),
    ...(degrees && { degrees }),
  };

  if (Object.keys(facets).length > 0) {
    return facets;
  }
}
