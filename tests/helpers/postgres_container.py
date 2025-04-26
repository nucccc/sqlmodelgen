import socket
import time
from contextlib import contextmanager

import docker
import psycopg

class PostgresContainer:

    def __init__(self):
        self.client = docker.from_env()
        self.image = 'postgres:16'
        self.host_port = 8111#self._find_free_port()
        self.container_port = 5432
        self.username = 'tester'
        self.password = 'password'
        self.database = 'test'
        self.container = None

    
    def start(self):
        self.container = self.client.containers.run(
            self.image,
            detach=True,
            environment={
                'POSTGRES_USER': self.username,
                'POSTGRES_PASSWORD': self.password,
                'POSTGRES_DB': self.database
            },
            hostname='127.0.0.1',
            ports={f'{self.container_port}/tcp': self.host_port},
            remove=True
        )
        self._wait_for_postgres()

    
    def stop(self):
        if self.container:
            self.container.stop()
            self.container = None

    
    def _find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
        
    
    def get_conn_string(self) -> str:
        return f"postgres://{self.username}:{self.password}@localhost:{self.host_port}/{self.database}"
    

    def _wait_for_postgres(self, n_attempts: int = 30, delay: int = 1):
        for _ in range(n_attempts):
            try:
                with psycopg.connect(self.get_conn_string()) as conn:
                    with conn.cursor() as cur:
                        cur.execute('SELECT 1')
                        break
            except (psycopg.OperationalError, psycopg.InterfaceError):
                pass
            time.sleep(delay)

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


@contextmanager
def postgres_container():
    """Context manager for PostgreSQL container."""
    container = PostgresContainer()
    try:
        container.start()
        yield container
    finally:
        container.stop()


# Example usage
if __name__ == "__main__":
    # Using context manager
    with postgres_container() as pg:
        print('entering')
        print(pg.get_conn_string())
        # ah = input()
        # print(ah)
        # print('going on')
        # Create a test table
        conn = psycopg.connect(pg.get_conn_string())
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE test_table (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        # Insert data
        cursor.execute("INSERT INTO test_table (name) VALUES ('test1'), ('test2')")
        
        # Query data
        cursor.execute("SELECT * FROM test_table")
        results = cursor.fetchall()
        print("Results:", results)
        
        # Direct connection
        # with pg.get_connection() as conn:
        #     with conn.cursor() as cur:
        #         cur.execute("SELECT * FROM test_table WHERE name = %s", ("test1",))
        #         print("Custom query:", cur.fetchall())