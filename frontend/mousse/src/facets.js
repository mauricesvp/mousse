export default {
    "Cycle": {
        "terms": {
            "field": "parts.cycle_str",
            "mincount": 0,
            "limit": 200,
            "sort": "index",
        }
    },
    "Type": {
        "terms": {
            "field": "parts.type_str",
            "limit": 200,
        }
    },
    "ECTS": {
        "terms": {
            "field": "ects",
            "limit": 200,
            // "sort": "index"

        }
    },
    "Degree": {
        "terms": {
            "field": "degrees.name_degree_str",
            "mincount": 0,
            "limit": 200,
            "sort": "index",
        }
    },
}
