import time
from contextlib import contextmanager
from dataclasses import dataclass

import docker
import mysql.connector


TEST_USER = 'root'
TEST_PSW = 'my-secret-pw'
TEST_HOST = 'localhost'
# TODO: maybe at a point this port exposed could randomically
# chosen to be a random one like in postgres
TEST_PORT = 3306


@dataclass 
class MySqlConnAttrs:
    user: str
    psw: str
    host: str
    port: int

    @property
    def conn_str(self) -> str:
        return f'mysql://{self.user}:{self.psw}@{self.host}:{self.port}'


def wait_until_conn(n_attempts: int = 100, delay: int = 1) -> mysql.connector.CMySQLConnection:
    for _ in range(n_attempts):
        try:
            conn = mysql.connector.connect(host=TEST_HOST, port=TEST_PORT, user=TEST_USER, password=TEST_PSW)
        except mysql.connector.errors.OperationalError:
            time.sleep(delay)
        else:
            return conn


@contextmanager
def mysql_docker():
    client = docker.from_env()
    container = client.containers.run(
        'mysql:9.5.0',
        detach=True,
        environment={
            'MYSQL_ROOT_PASSWORD':TEST_PSW
        },
        ports={'3306/tcp': TEST_PORT},
        hostname=TEST_HOST,
        remove=True,
    )
    try:
        container.start()
        conn = wait_until_conn()
        conn_data = MySqlConnAttrs(
            user=TEST_USER,
            psw=TEST_PSW,
            host=TEST_HOST,
            port=TEST_PORT,
        )
        yield (container, conn, conn_data)
    finally:
        container.stop()
        conn.close()
    client.close()