from db.db_connector import DBConnector
from db.dynamodb_connector import DynamoDBConnector
from db.mysql_connector import MySQLConnector
from db.pg_connector import PGConnector
from db.rds_connector import RDSConnector
from db.redshift_connector import RedshiftConnector
from db.redshift_serverless_connector import RedshiftServerlessConnector


def db_connector_factory(config, env) -> DBConnector:
    db_type = config[env].get("type", "postgres")
    connector_classes = {
        "postgres": PGConnector,
        "mysql": MySQLConnector,
        "redshift": RedshiftConnector,
        "redshift_serverless": RedshiftServerlessConnector,
        "dynamodb": DynamoDBConnector,
        "rds": RDSConnector,
    }
    try:
        connector_class = connector_classes[db_type]
        return connector_class(config=config, env=env)
    except KeyError:
        raise ValueError(f"Unsupported database type: {db_type}")
