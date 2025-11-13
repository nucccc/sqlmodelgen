import time
from contextlib import contextmanager

import docker
import mysql.connector


def wait_until_conn(n_attempts: int = 100, delay: int = 1) -> mysql.connector.CMySQLConnection:
    for _ in range(n_attempts):
        try:
            conn = mysql.connector.connect(host='localhost', port=3306, user='root', password='my-secret-pw')
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
            "MYSQL_ROOT_PASSWORD":"my-secret-pw"
        },
        ports={f'3306/tcp': 3306},
        hostname='127.0.0.1',
        remove=True,
    )
    try:
        container.start()
        conn = wait_until_conn()
        yield (container, conn)
    finally:
        container.stop()
        conn.close()
    client.close()