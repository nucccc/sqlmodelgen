'''
this test module shall verify that code generation from direct connection
with postgres works
'''

import psycopg
import docker

from sqlmodelgen import gen_code_from_postgres

from helpers.helpers import collect_code_info
from helpers.postgres_container import postgres_container
        

def test_gen_code():

    with postgres_container() as pgc:
        with psycopg.connect(pgc.get_conn_string()) as conn:
            cursor = conn.cursor()

            cursor.execute('''CREATE TABLE users(
    id uuid NOT NULL,
    PRIMARY KEY (id),
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    psw_hash TEXT NOT NULL,
    registered_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE leagues(
    id uuid PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    public BOOLEAN NOT NULL
);

CREATE TABLE participations(
    admin BOOLEAN NOT NULL,
    user_id uuid,
    FOREIGN KEY (user_id) REFERENCES users(id),
    league_id uuid,
    FOREIGN KEY (league_id) REFERENCES leagues(id),
    PRIMARY KEY (user_id, league_id)
);

CREATE TABLE invitations(
    invitee_id uuid,
    FOREIGN KEY (invitee_id) REFERENCES users(id),
    league_id uuid,
    FOREIGN KEY (league_id) REFERENCES leagues(id),
    inviter_id uuid,
    FOREIGN KEY (inviter_id) REFERENCES users(id),
    PRIMARY KEY (invitee_id, league_id)
);

CREATE TABLE nations(
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE athletes(
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    nation_id BIGSERIAL,
    FOREIGN KEY (nation_id) REFERENCES nations(id),
    height INTEGER,
    weight INTEGER,
    bio TEXT,
    nickname TEXT
);''')
            conn.commit()

        code_generated = gen_code_from_postgres(pgc.get_conn_string(), generate_relationships=True)

        assert collect_code_info(code_generated) == collect_code_info('''from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from uuid import UUID, uuid4
from datetime import datetime

                                                                      
class Users(SQLModel, table=True):
    __tablename__ = 'users'
    __table_args__ = [UniqueConstraint('email'), UniqueConstraint('name')]
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    email: str
    name: str
    psw_hash: str
    registered_at: datetime
    participationss: list['Participations'] = Relationship(back_populates='user')
    invitationss: list['Invitations'] = Relationship(back_populates='invitee')
    invitationss0: list['Invitations'] = Relationship(back_populates='inviter')

class Participations(SQLModel, table=True):
    __tablename__ = 'participations'
    admin: bool
    user_id: UUID = Field(primary_key=True, foreign_key='users.id', default_factory=uuid4)
    league_id: UUID = Field(primary_key=True, foreign_key='leagues.id', default_factory=uuid4)
    user: 'Users' | None = Relationship(back_populates='participationss')
    league: 'Leagues' | None = Relationship(back_populates='participationss')

class Leagues(SQLModel, table=True):
    __tablename__ = 'leagues'
    __table_args__ = [UniqueConstraint('name')]
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    name: str
    public: bool
    participationss: list['Participations'] = Relationship(back_populates='league')
    invitationss: list['Invitations'] = Relationship(back_populates='league')

class Invitations(SQLModel, table=True):
    __tablename__ = 'invitations'
    invitee_id: UUID = Field(primary_key=True, foreign_key='users.id', default_factory=uuid4)
    league_id: UUID = Field(primary_key=True, foreign_key='leagues.id', default_factory=uuid4)
    inviter_id: UUID | None = Field(foreign_key='users.id', default_factory=uuid4)
    invitee: 'Users' | None = Relationship(back_populates='invitationss')
    league: 'Leagues' | None = Relationship(back_populates='invitationss')
    inviter: 'Users' | None = Relationship(back_populates='invitationss0')

class Nations(SQLModel, table=True):
    __tablename__ = 'nations'
    id: int = Field(primary_key=True)
    name: str
    athletess: list['Athletes'] = Relationship(back_populates='nation')

class Athletes(SQLModel, table=True):
    __tablename__ = 'athletes'
    id: int = Field(primary_key=True)
    name: str
    nation_id: int = Field(foreign_key='nations.id')
    height: int | None
    weight: int | None
    bio: str | None
    nickname: str | None
    nation: 'Nations' | None = Relationship(back_populates='athletess')''')
