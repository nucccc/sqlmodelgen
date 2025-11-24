import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

import docker
import mysql.connector


@dataclass
class MySqlConnAggregate:
    container: docker.models.containers.Container # Any # TODO: find appropriate container type
    conn: mysql.connector.CMySQLConnection
    user: str
    psw: str
    port: int


def wait_until_conn(
    host: str,
    port: int,
    user: str,
    psw: str,
    n_attempts: int = 100,
    delay: int = 1,
) -> mysql.connector.CMySQLConnection:
    for _ in range(n_attempts):
        try:
            conn = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=psw,
            )
        except mysql.connector.errors.OperationalError:
            time.sleep(delay)
        else:
            return conn


@contextmanager
def mysql_docker(
    port: int = 3306,
    user: str = 'root',
    psw: str = 'my-secret-pw',
):
    client = docker.from_env()
    container = client.containers.run(
        'mysql:9.5.0',
        detach=True,
        environment={
            'MYSQL_ROOT_PASSWORD':psw
        },
        ports={'3306/tcp': port},
        hostname='127.0.0.1',
        remove=True,
    )
    try:
        container.start()
        conn = wait_until_conn(
            host = 'localhost',
            port = port,
            user = user,
            psw = psw,
        )
        yield MySqlConnAggregate(
            container=container,
            conn=conn,
            psw=psw,
            port=port,
            user=user
        )
    finally:
        container.stop()
        conn.close()
    client.close()