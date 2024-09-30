def validate_db_config(config_data):
    REQUIRED_FIELDS = {
        "postgres": ["type", "host", "port", "dbname", "user", "password"],
        "mysql": ["type", "host", "port", "dbname", "user", "password"],
        "rds": [
            "type",
            "region",
            "profile",
            "host",
            "dbname",
            "secret_arn",
            "bucket_name",
            "object_key",
            "iam_role",
        ],
        "redshift_serverless": [
            "type",
            "region",
            "profile",
            "host",
            "dbname",
            "bucket_name",
            "object_key",
            "iam_role",
        ],
        "redshift": [
            "type",
            "region",
            "profile",
            "host",
            "dbname",
            "bucket_name",
            "object_key",
            "iam_role",
        ],
        "dynamodb": [
            "type",
            "region",
            "profile",
            "bucket_name",
            "object_key",
            "source_table",
        ],
    }

    errors = []

    for config_name, config in config_data.items():
        config_type = config.get("type")
        if config_type not in REQUIRED_FIELDS:
            errors.append(
                f"database.yaml: In '{config_name}', the 'type' '{config_type}' is invalid."
            )
            continue  # Skip further validation for this config
        required_fields = REQUIRED_FIELDS[config_type]
        for field in required_fields:
            if field not in config:
                errors.append(
                    f"database.yaml: In '{config_name}' of type '{config_type}', missing required field '{field}'."
                )

    return errors


def validate_settings(settings_data):
    REQUIRED_SETTINGS = {
        "data_generation": {
            "database": ["batch_size", "commit_interval"],
            "csv": ["delimiter", "include_headers", "batch_size"],
            "json": ["batch_size"],
        },
        "logging": {"level": []},
    }

    errors = []

    # Check for top-level 'settings' key
    if "settings" not in settings_data:
        errors.append("settings.yaml: Missing top-level 'settings' section.")
        return errors  # Cannot proceed without 'settings' key

    settings = settings_data["settings"]

    for section_name, subsections in REQUIRED_SETTINGS.items():
        if section_name not in settings:
            errors.append(
                f"settings.yaml: Missing section '{section_name}' in 'settings'."
            )
            continue  # Skip to next section
        section = settings[section_name]

        for subsection_name, required_fields in subsections.items():
            if subsection_name not in section:
                errors.append(
                    f"settings.yaml: Missing subsection '{subsection_name}' in 'settings.{section_name}'."
                )
                continue  # Skip to next subsection
            subsection = section[subsection_name]

            for field in required_fields:
                if field not in subsection:
                    errors.append(
                        f"settings.yaml: In 'settings.{section_name}.{subsection_name}', missing required field '{field}'."
                    )

    return errors


ALLOWED_TYPES = ["integer", "float", "string", "timestamp", "boolean", "json", "list"]
ALLOWED_METHODS = ["sequence", "random"]

VALIDATION_RULES = {
    # Existing types with methods
    ("integer", "sequence"): {
        "required": [],
        "optional": [
            "start",
            "end",
            "values",
            "interval",
            "foreign_table",
            "foreign_key",
        ],
        "not_allowed": ["decimal_places", "struct", "size", "inner_type"],
    },
    ("integer", "random"): {
        "required": [],
        "optional": [
            "start",
            "end",
            "values",
            "interval",
            "foreign_table",
            "foreign_key",
        ],
        "not_allowed": ["decimal_places", "struct", "size", "inner_type"],
    },
    ("float", "sequence"): {
        "required": [],
        "optional": [
            "start",
            "end",
            "values",
            "interval",
            "decimal_places",
            "foreign_table",
            "foreign_key",
        ],
        "not_allowed": ["struct", "size", "inner_type"],
    },
    ("float", "random"): {
        "required": [],
        "optional": [
            "start",
            "end",
            "values",
            "interval",
            "decimal_places",
            "foreign_table",
            "foreign_key",
        ],
        "not_allowed": ["struct", "size", "inner_type"],
    },
    ("string", "sequence"): {
        "required": [],
        "optional": ["values", "foreign_table", "foreign_key"],
        "not_allowed": [
            "start",
            "end",
            "interval",
            "decimal_places",
            "struct",
            "size",
            "inner_type",
        ],
    },
    ("string", "random"): {
        "required": [],
        "optional": [
            "start",
            "end",
            "values",
            "interval",
            "foreign_table",
            "foreign_key",
        ],
        "not_allowed": ["decimal_places", "struct", "size", "inner_type"],
    },
    ("timestamp", "sequence"): {
        "required": [],
        "optional": [
            "start",
            "end",
            "values",
            "interval",
            "foreign_table",
            "foreign_key",
        ],
        "not_allowed": ["decimal_places", "struct", "size", "inner_type"],
    },
    ("timestamp", "random"): {
        "required": [],
        "optional": [
            "start",
            "end",
            "values",
            "interval",
            "foreign_table",
            "foreign_key",
        ],
        "not_allowed": ["decimal_places", "struct", "size", "inner_type"],
    },
    ("boolean", "sequence"): {
        "required": [],
        "optional": ["values", "foreign_table"],
        "not_allowed": [
            "start",
            "end",
            "interval",
            "decimal_places",
            "foreign_key",
            "struct",
            "size",
            "inner_type",
        ],
    },
    ("boolean", "random"): {
        "required": [],
        "optional": ["values", "foreign_table"],
        "not_allowed": [
            "start",
            "end",
            "interval",
            "decimal_places",
            "foreign_key",
            "struct",
            "size",
            "inner_type",
        ],
    },
    # 'json' type doesn't use 'method', requires 'struct'
    ("json", None): {
        "required": ["struct"],
        "optional": [],
        "not_allowed": [
            "method",
            "start",
            "end",
            "values",
            "interval",
            "decimal_places",
            "foreign_table",
            "foreign_key",
            "size",
            "inner_type",
        ],
    },
    # 'list' type doesn't use 'method', requires 'size' and 'inner_type'
    ("list", None): {
        "required": ["size", "inner_type", "generation"],
        "optional": [
            "start",
            "end",
            "values",
            "interval",
            "decimal_places",
            "foreign_table",
            "foreign_key",
        ],
        "not_allowed": [
            "struct",
        ],
    },
    ("list", "sequence"): {
        "required": ["size", "inner_type", "generation"],
        "optional": [
            "start",
            "end",
            "values",
            "interval",
            "decimal_places",
            "foreign_table",
            "foreign_key",
        ],
        "not_allowed": [
            "struct",
        ],
    },
    ("list", "random"): {
        "required": ["size", "inner_type", "generation"],
        "optional": [
            "start",
            "end",
            "values",
            "decimal_places",
            "foreign_table",
            "foreign_key",
        ],
        "not_allowed": [
            "struct",
        ],
    },
}


def validate_data_definition(data):
    errors = []

    if "tables" not in data:
        errors.append("Missing 'tables' key in the data definition.")
        return errors  # Cannot proceed without 'tables' key

    if not isinstance(data["tables"], list):
        errors.append("'tables' should be a list.")
        return errors  # Cannot proceed without a proper 'tables' list

    for table in data["tables"]:
        table_errors = validate_table(table)
        errors.extend(table_errors)

    return errors


def validate_table(table):
    errors = []
    table_name = table.get("name", "<unknown>")
    if "name" not in table:
        errors.append("Each table must have a 'name' field.")
    if "row_count" not in table:
        errors.append(f"Table '{table_name}' is missing 'row_count' field.")
    if "columns" not in table:
        errors.append(f"Table '{table_name}' is missing 'columns' field.")
        return errors  # Cannot proceed without 'columns' key

    if not isinstance(table["columns"], list):
        errors.append(f"Table '{table_name}' 'columns' should be a list.")
        return errors  # Cannot proceed without a proper 'columns' list

    for column in table["columns"]:
        column_errors = validate_column(column, table_name)
        errors.extend(column_errors)

    return errors


def validate_column(column, table_name, context="column"):
    errors = []
    if "name" not in column:
        errors.append(
            f"{context.capitalize()} in table '{table_name}' is missing 'name' field."
        )
        return errors  # Cannot proceed without 'name'

    column_name = column["name"]

    if "type" not in column:
        errors.append(
            f"{context.capitalize()} '{column_name}' in table '{table_name}' is missing 'type' field."
        )
        return errors  # Cannot proceed without 'type'

    column_type = column["type"]

    if column_type not in ALLOWED_TYPES:
        errors.append(
            f"{context.capitalize()} '{column_name}' in table '{table_name}' has invalid type '{column_type}'."
        )
        return errors  # Cannot proceed with invalid type

    if column_type == "json":
        key = (column_type, None)
        rules = VALIDATION_RULES[key]
        # Check required fields
        for field in rules["required"]:
            if field not in column:
                errors.append(
                    f"{context.capitalize()} '{column_name}' in table '{table_name}' is missing required field '{field}'."
                )
        # Check not allowed fields
        for field in rules["not_allowed"]:
            if field in column:
                errors.append(
                    f"{context.capitalize()} '{column_name}' in table '{table_name}' should not have field '{field}'."
                )
        # Validate the struct recursively
        if "struct" in column:
            if not isinstance(column["struct"], list):
                errors.append(
                    f"The 'struct' field in '{column_name}' of table '{table_name}' must be a list."
                )
            else:
                for sub_column in column["struct"]:
                    sub_column_errors = validate_column(
                        sub_column, table_name, context=f"sub-column of '{column_name}'"
                    )
                    errors.extend(sub_column_errors)
    elif column_type == "list":
        key = (column_type, None)
        rules = VALIDATION_RULES[key]
        # Check required fields
        for field in rules["required"]:
            if field not in column:
                errors.append(
                    f"{context.capitalize()} '{column_name}' in table '{table_name}' is missing required field '{field}'."
                )
        # Check not allowed fields
        for field in rules["not_allowed"]:
            if field in column:
                errors.append(
                    f"{context.capitalize()} '{column_name}' in table '{table_name}' should not have field '{field}'."
                )
        # Validate 'generation' field
        if "generation" in column:
            generation_errors = validate_generation(
                column["generation"], column, table_name, context
            )
            errors.extend(generation_errors)
        # Validate 'inner_type' and 'size'
        if column["inner_type"] not in ALLOWED_TYPES:
            errors.append(
                f"'inner_type' of {context} '{column_name}' in table '{table_name}' is invalid."
            )
    else:
        # For other types, validate 'generation' field
        if "generation" not in column:
            errors.append(
                f"{context.capitalize()} '{column_name}' in table '{table_name}' is missing 'generation' field."
            )
        else:
            generation_errors = validate_generation(
                column["generation"], column, table_name, context
            )
            errors.extend(generation_errors)

    return errors


def validate_generation(generation, column, table_name, context):
    errors = []
    if "method" not in generation:
        errors.append(
            f"{context.capitalize()} '{column['name']}' in table '{table_name}' generation is missing 'method' field."
        )
        return errors  # Cannot proceed without 'method'

    method = generation["method"]
    column_type = column["type"]

    if method not in ALLOWED_METHODS:
        errors.append(
            f"{context.capitalize()} '{column['name']}' in table '{table_name}' generation has invalid method '{method}'."
        )
        return errors  # Cannot proceed with invalid method

    key = (column_type, method)

    if key not in VALIDATION_RULES:
        errors.append(
            f"{context.capitalize()} '{column['name']}' in table '{table_name}' has unsupported type '{column_type}' and method '{method}' combination."
        )
        return errors  # Cannot proceed with invalid combination

    rules = VALIDATION_RULES[key]

    # Allowed fields in generation
    allowed_fields = set(rules["required"] + rules["optional"] + ["method"])
    for field in generation:
        if field not in allowed_fields:
            if field != "method":
                errors.append(
                    f"{context.capitalize()} '{column['name']}' in table '{table_name}' generation has invalid field '{field}' for type '{column_type}' and method '{method}'."
                )

    # Check that disallowed fields are not present
    for field in rules.get("not_allowed", []):
        if field in generation:
            errors.append(
                f"{context.capitalize()} '{column['name']}' in table '{table_name}' generation field '{field}' is not allowed for type '{column_type}' and method '{method}'."
            )

    # Enforce special conditions
    # For 'random' method, either 'start' and 'end' or 'values' must be set
    if method == "random":
        if "values" in generation:
            pass  # 'values' is set
        elif "start" in generation and "end" in generation:
            pass  # 'start' and 'end' are set
        else:
            errors.append(
                f"{context.capitalize()} '{column['name']}' in table '{table_name}' with 'random' method must have either 'values' or both 'start' and 'end' defined."
            )

    # For 'sequence' of 'timestamp' type, either 'start' or 'values' must be set
    if method == "sequence" and column_type == "timestamp":
        if "start" in generation or "values" in generation:
            pass
        else:
            errors.append(
                f"{context.capitalize()} '{column['name']}' in table '{table_name}' of type 'timestamp' with 'sequence' method must have 'start' or 'values' defined."
            )

    # If 'values' is set, 'start', 'end', 'interval' should not be set
    if "values" in generation:
        for field in ["start", "end", "interval"]:
            if field in generation:
                errors.append(
                    f"{context.capitalize()} '{column['name']}' in table '{table_name}' cannot have '{field}' defined when 'values' is set."
                )

    # If 'foreign_table' and 'foreign_key' are set, they are used as 'values'
    if "foreign_table" in generation and "foreign_key" in generation:
        for field in ["values", "start", "end", "interval"]:
            if field in generation:
                errors.append(
                    f"{context.capitalize()} '{column['name']}' in table '{table_name}' cannot have '{field}' defined when 'foreign_table' and 'foreign_key' are set."
                )
    elif "foreign_table" in generation or "foreign_key" in generation:
        errors.append(
            f"{context.capitalize()} '{column['name']}' in table '{table_name}' must have both 'foreign_table' and 'foreign_key' defined together."
        )

    # If 'type' is 'float' and 'decimal_places' is set, it must be an integer
    if column_type == "float" and "decimal_places" in generation:
        if not isinstance(generation["decimal_places"], int):
            errors.append(
                f"{context.capitalize()} '{column['name']}' in table '{table_name}' has 'decimal_places' which must be an integer."
            )

    # For 'timestamp' type with 'random' method, 'start' and 'end' are required unless 'values' is set
    if column_type == "timestamp" and method == "random":
        if "values" not in generation and (
            "start" not in generation or "end" not in generation
        ):
            errors.append(
                f"{context.capitalize()} '{column['name']}' in table '{table_name}' of type 'timestamp' with 'random' method must have both 'start' and 'end' defined or 'values'."
            )

    return errors
