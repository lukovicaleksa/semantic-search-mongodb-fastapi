from pymongo import MongoClient, database
from pymongo.errors import ConnectionFailure, OperationFailure


class MongoDBAtlasConnection:
    """
    Mongo DB Atlas Connection
    """
    def __init__(self, username: str, password: str, host: str, db_name: str) -> None:
        """
        Mongo DB Atlas Connection

        :param username: User - username
        :param password: User - password
        :param host: Mongo DB Hostname
        :param db_name: DB name
        """
        self.connection_str = f'mongodb+srv://{username}:{password}@{host}/?retryWrites=true&w=majority'
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self, server_selection_timeout_ms: int = 5000) -> None:
        """
        Establish DB Connection

        :param server_selection_timeout_ms: Server selection timeout [ms]
        """
        try:
            self.client = MongoClient(host=self.connection_str, serverSelectionTimeoutMS=server_selection_timeout_ms)
            self.db = self.client[self.db_name]

            # check connection by running a simple command
            self.client.admin.command('ismaster')
        except (ConnectionFailure, OperationFailure) as err:
            raise ConnectionError(f'Failed to connect to database: {err}')

    def get_db(self) -> database.Database:
        """
        Get Mongo DB Object

        :return: DB Object
        """
        return self.db

    def close_connection(self) -> None:
        """
        Close DB Connection
        """
        if self.client:
            self.client.close()
