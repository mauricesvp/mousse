"""
Mousse database (wrapper).

mauricesvp 2021
"""
import os

import mysql.connector
from mysql.connector.connection_cext import CMySQLConnection
from mysql.connector.cursor_cext import CMySQLCursor

from mousse.log import setup_logger
from mousse.utils import retry

PASSWORD = os.environ.get("MYSQL_ROOT_PASSWORD")
MYSQL_DB = os.environ.get("MYSQL_DATABASE")

logger = setup_logger("mousse_db")


class MousseDB:
    """
    Mousse database.

    Wraps mysql and adds data export.
    """

    db: CMySQLConnection = None
    cursor: CMySQLCursor = None

    def __init__(self) -> None:
        """Init instance."""
        if not self.db:
            self.db = self.get_db()
        self.cursor = self.db.cursor()

    @retry(5)
    def get_db(self) -> mysql.connector.connection_cext.CMySQLConnection:
        """Return mysql connection."""
        return mysql.connector.connect(
            host="mysql", password=PASSWORD, database=MYSQL_DB
        )

    def get_cursor(self) -> mysql.connector.cursor_cext.CMySQLCursor:
        """Return connection cursor."""
        if not self.db:
            return self.get_db().cursor()
        return self.db.cursor()

    @retry(5)
    def health_check(self) -> None:
        """Reconnect if necessary."""
        if not self.db:
            self.db = self.get_db()
        if not self.cursor:
            self.cursor = self.get_cursor()

    def add_module(self, val: dict) -> None:
        """Add single module."""
        self.add_modules([val])

    def add_modules(self, val: list) -> None:
        """Add multiple modules."""
        logger.info(f"Adding {len(val)} modules.")
        # TODO: Verify that values are well-formed?
        self.health_check()
        self.cursor = self.get_cursor()

        # Convert list of dicts into list of tuples
        modules = [
            (
                int(m["id"]),
                m["name"],
                int(m["version"]),
                m["language"],
                int(m["ects"]),
                m["exam_type_str"],
                m["faculty"],
                m["institute"],
                m["group_str"],
            )
            for m in val
        ]

        sql_modules = """
        REPLACE INTO modules
        (id, name, version, language, ects, exam_type_str,
        faculty, institute, group_str)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.executemany(sql_modules, modules)
        self.db.commit()

        sql_parts = """
        REPLACE INTO module_parts (module_id, name, module_type, cycle)
        VALUES (%s, %s, %s, %s)
        """
        module_tmp = [(x["id"], x["module_parts"]) for x in val]
        module_parts = []
        for m in module_tmp:
            for part in m[1]:
                module_parts.append(
                    (int(m[0]), part["name"], part["module_type"], part["cycle"])
                )
        self.cursor.executemany(sql_parts, module_parts)
        self.db.commit()

        self.cursor.close()

    def add_degree(self, val: dict) -> None:
        """Add single degree."""
        logger.info("Adding degree.")
        # TODO: Verify that values are well-formed?
        self.health_check()
        self.cursor = self.get_cursor()

        degree = (
            int(val["id"]),
            val["name"],
            val["semester"],
            val["ba_or_ma"],
            val["stupo"],
        )

        sql_degree = """
        REPLACE INTO degrees (id, name, semester, ba_or_ma, stupo)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.cursor.execute(sql_degree, degree)
        self.db.commit()

        sql_delete_degree_modules = """
        DELETE FROM degree_modules WHERE degree_id = %s
        """
        self.cursor.execute(sql_delete_degree_modules, (degree[0],))
        self.db.commit()

        degree_modules = [
            (int(val["id"]), int(x[0].replace("#", ""))) for x in val["modules"]
        ]
        sql_degree_modules = """
        REPLACE INTO degree_modules (degree_id, module_id)
        VALUES (%s, %s)
        """
        self.cursor.executemany(sql_degree_modules, degree_modules)
        self.db.commit()

        self.cursor.close()

    def get_info(self) -> list:
        """Return data as list of modules."""
        logger.info("Getting info.")
        self.health_check()
        cursor_buffered = self.db.cursor(buffered=True)
        cursor_tmp = self.db.cursor()

        sql_find_modules = """
            SELECT id, name, version, language, ects, exam_type_str,
            faculty, institute, group_str FROM modules"""
        cursor_buffered.execute(sql_find_modules)
        module = cursor_buffered.fetchone()
        modules = []
        while module:
            module_id = module[0]
            name = module[1]
            version = int(module[2])
            language = module[3]
            ects = int(module[4])
            exam_type_str = module[5]
            faculty = module[6]
            institute = module[7]
            group = module[8]

            sql_find_parts = f"""
            SELECT modules.*, module_parts.*
            FROM modules
            LEFT JOIN module_parts on modules.id = module_parts.module_id
            WHERE module_id = {module_id}
            """
            cursor_tmp.execute(sql_find_parts)
            parts = cursor_tmp.fetchall()
            sql_find_degrees = f"""
            SELECT modules.id, degrees.id,
            degrees.name, degrees.semester,
            degrees.ba_or_ma, degrees.stupo
            FROM degree_modules
            LEFT JOIN degrees on degree_modules.degree_id = degrees.id
            LEFT JOIN modules on degree_modules.module_id = modules.id
            WHERE module_id = {module_id}
            """
            cursor_tmp.execute(sql_find_degrees)
            degrees = cursor_tmp.fetchall()
            # Build module
            if len(parts) > 0:
                parts_ = [
                    {
                        "name_part": x[10],
                        "type": x[11],
                        "cycle": x[12],
                    }
                    for x in parts
                ]
            else:
                parts_ = []
            if len(degrees) > 0:
                degrees_ = [
                    {
                        "name_degree": x[2],
                        "semester_degree": x[3],
                        "bama": x[4],
                        "stupo": x[5],
                    }
                    for x in degrees
                ]
            else:
                degrees_ = []

            module_ = {
                "id": module_id,
                "name": name,
                "version": version,
                "language": language,
                "ects": str(ects),
                "parts": parts_,
                "degrees": degrees_,
                "exam_type_str": exam_type_str,
                "faculty": faculty,
                "institute": institute,
                "group_str": group,
            }
            modules.append(module_)

            module = cursor_buffered.fetchone()
        logger.info(f"Returning info for {len(modules)} modules.")
        return modules
