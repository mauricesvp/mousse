USE moussedb;
CREATE TABLE modules (
        id int NOT NULL,
        name char(255) NOT NULL,
        version int,
        language char(64),
        ects int,
        PRIMARY KEY (id),
        INDEX (id)
);
CREATE TABLE module_parts (
        module_id int NOT NULL,
        name char(255) NOT NULL,
        module_type char(255),
        cycle char(64),
        INDEX mod_id (module_id),
        FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE degrees (
        id int NOT NULL,
        name char(255) NOT NULL,
        semester char(64),
        ba_or_ma char(64),
        stupo char(64),
        PRIMARY KEY (id),
        INDEX (id),
        INDEX (name)
);
CREATE TABLE degree_modules (
        degree_id int NOT NULL,
        module_id int NOT NULL,
        PRIMARY KEY (degree_id, module_id),
        INDEX (module_id, degree_id)
);
