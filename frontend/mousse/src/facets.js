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
            "mincount": 0,
        }
    },
    "ECTS": {
        "terms": {
            "field": "ects_str",
            "limit": 200,
            "mincount": 0,
            "sort": "index"

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
    "Department": {
        "terms": {
            "field": "faculty_str",
            "mincount": 0,
            "limit": 200,
            "sort": "index",
            "facet": {
                "Institute": {
                    "type": "terms",
                    "field": "institute_str",
                    "limit": 200,
                    "sort": "index",
                    "facet": {
                        "Group": {
                            "type": "terms",
                            "field": "group_str",
                            "limit": 200,
                            "sort": "index",
                        }
                    }
                }
            }
        }
    },
    "Exam Type": {
        "terms": {
            "field": "exam_type_str",
            "mincount": 0,
            "limit": 200,
            "sort": "index",
        }
    },
}
