from db.db_connector import DBConnector
from db.dynamodb_connector import DynamoDBConnector
from db.mysql_connector import MySQLConnector
from db.pg_connector import PGConnector
from db.redshift_connector import RedshiftConnector
from db.redshift_serverless_connector import RedshiftServerlessConnector
from db.rds_connector import RDSConnector

def db_connector_factory(config, env) -> DBConnector:
    db_type = config[env].get('type', 'postgres')
    if db_type == 'postgres':
        return PGConnector(config=config, env=env)
    elif db_type == 'mysql':
        return MySQLConnector(config=config, env=env)
    elif db_type == 'redshift':
        return RedshiftConnector(config=config, env=env)
    elif db_type == 'redshift_serverless':
        return RedshiftServerlessConnector(config=config, env=env)
    elif db_type == 'dynamodb':
        return DynamoDBConnector(config=config, env=env)
    elif db_type == 'rds':
        return RDSConnector(config=config, env=env)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
