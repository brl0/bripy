"""Database helpers."""

class conn_str_info:
    """Connection string builder."""

    driver = 'sqlite'
    is_absolute = False
    user = None
    password = None
    server = 'localhost'
    port = '3306'
    db_name = 'information_schema'

    def __init__(self):
        pass

    def get_conn_str(self):
        pass
