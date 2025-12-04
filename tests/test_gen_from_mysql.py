import time

import mysql.connector

from sqlmodelgen import gen_code_from_mysql

from helpers.helpers import collect_code_info
from helpers.mysql_container import mysql_docker


def test_mysql():
    with mysql_docker() as (mysqld, conn):
        cur = conn.cursor()

        sqls = ['''CREATE TABLE IF NOT EXISTS Hero (
            id INT, 
            name VARCHAR(255), 
            secret_name VARCHAR(255) UNIQUE, 
            age INT
        );''',        
        '''CREATE TABLE Persons (
            ID int NOT NULL,
            LastName varchar(255) NOT NULL,
            FirstName varchar(255),
            Age int,
            PRIMARY KEY (ID)
        );''']

        cur.execute('CREATE DATABASE IF NOT EXISTS nucdb')

        cur.execute('USE nucdb')

        for sql in sqls:
            cur.execute(sql)

        conn.commit()

        code = gen_code_from_mysql(conn, 'nucdb')

        print(code)

        expected_code ='''from sqlmodel import SQLModel, Field, UniqueConstraint

class Hero(SQLModel, table=True):
    __tablename__ = 'Hero'
    __table_args__ = (UniqueConstraint('secret_name'), )
    id: int | None
    name: str | None
    secret_name: str | None
    age: int | None

class Persons(SQLModel, table=True):
    __tablename__ = 'Persons'
    ID: int = Field(primary_key=True)
    LastName: str
    FirstName: str | None
    Age: int | None'''
        
        assert collect_code_info(code) == collect_code_info(expected_code)


def test_mysql_fk_rel():
    with mysql_docker() as (mysqld, conn):
        cur = conn.cursor()

        sqls = ['''CREATE TABLE nations(
            id INT PRIMARY KEY,
            name TEXT NOT NULL
        );''',
        '''CREATE TABLE athletes(
            id INT PRIMARY KEY,
            name TEXT NOT NULL,
            nation_id INT,
            FOREIGN KEY (nation_id) REFERENCES nations(id),
            height INTEGER,
            weight INTEGER,
            bio TEXT,
            nickname TEXT
        );''']

        cur.execute('CREATE DATABASE IF NOT EXISTS nucdb')

        cur.execute('USE nucdb')

        for sql in sqls:
            cur.execute(sql)

        conn.commit()

        code = gen_code_from_mysql(conn, 'nucdb')

        print(code)

        expected_code ='''from sqlmodel import SQLModel, Field

class Athletes(SQLModel, table=True):
    __tablename__ = 'athletes'
    id: int = Field(primary_key=True)
    name: str
    nation_id: int | None = Field(foreign_key='nations.id')
    height: int | None
    weight: int | None
    bio: str | None
    nickname: str | None

class Nations(SQLModel, table=True):
    __tablename__ = 'nations'
    id: int = Field(primary_key=True)
    name: str'''
        
        assert collect_code_info(code) == collect_code_info(expected_code)
