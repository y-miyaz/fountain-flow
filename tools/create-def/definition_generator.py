import logging
import os
import sqlite3

import sqlparse
import yaml


def classify_type(table_info):
    try:
        classified_columns = []
        columns = [list(column) for column in table_info["columns"]]
        with open("config/classification.yaml", "r") as file:
            classification = yaml.safe_load(file)
        for column in columns:
            type = column[2].split("(")[0].lower()
            column[2] = classification.get(type, "string")
        with open("config/templates.yaml", "r") as file:
            templates = yaml.safe_load(file)
        for column in columns:
            column_name = column[1]
            classified_column = templates[column[2]].copy()
            classified_column["name"] = column_name
            classified_columns.append(classified_column)
        table_info["columns"] = classified_columns
        return table_info
    except Exception as error:
        raise error


def create_data_definitions(tables):
    try:
        definition = {"tables": tables}
        yaml.Dumper.ignore_aliases = lambda self, data: True
        with open("../../def/data.yaml", "w") as file:
            yaml.dump(definition, file, Dumper=yaml.Dumper, sort_keys=False)
    except Exception as error:
        raise error


def create_table_from_ddl(file_path, db_path):
    # データベースに接続
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # DDLファイルからSQLコマンドを読み込む
        with open(file_path, "r") as file:
            ddl = file.read()

        # DDLを実行してテーブルを作成
        cursor.executescript(ddl)
        conn.commit()
    except Exception as error:
        raise error
    finally:
        cursor.close()
        conn.close()


def get_table_definition(table_name, db_path):
    # データベースに接続
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # テーブルの定義を取得するSQLクエリを実行
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        columns = cursor.fetchall()

        return columns
    except Exception as error:
        logging.error(error)
    finally:
        cursor.close()
        conn.close()
        os.remove(db_path)


def get_table_name(tokens):
    for token in reversed(tokens):
        if token.ttype is None:
            return token.value
    return " "


def get_ddl_definition(file_path):
    try:
        with open(file_path, "r") as file:
            content = file.read()

        table_name = ""
        parse = sqlparse.parse(content)
        for stmt in parse:
            tokens = [
                t
                for t in sqlparse.sql.TokenList(stmt.tokens)
                if t.ttype != sqlparse.tokens.Whitespace
            ]
            is_create_stmt = False
            for i, token in enumerate(tokens):
                if token.match(sqlparse.tokens.DDL, "CREATE"):
                    is_create_stmt = True
                    continue

                if is_create_stmt and token.value.startswith("("):
                    table_name = get_table_name(tokens[:i])
                    break
            break
        create_table_from_ddl(file_path, "ddl.db")
        columns = get_table_definition(table_name, "ddl.db")
        table_info = {"name": table_name, "row_count": 10000, "columns": columns}

        return table_info
    except Exception as error:
        raise error
