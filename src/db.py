import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, declarative_base
from contextlib import contextmanager
from sqlalchemy import Column, String, ForeignKey
import bcrypt
import uuid
from typing import Tuple, Any, Optional
import sys


USER = os.environ.get('MYSQL_USER')
HOST = os.environ.get('MYSQL_HOST')
PASSWORD = os.environ.get('MYSQL_PASSWORD')
NAME = os.environ.get('MYSQL_DATABASE')
CHARSET = 'charset=utf8mb4'
DB_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{NAME}?{CHARSET}"


engine = create_engine(DB_URL)


Session = scoped_session(
    session_factory=sessionmaker(
        autocommit=False, autoflush=True,
        bind=engine, expire_on_commit=False,
    )
)


Base = declarative_base()


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# Consts
NAME_LENGTH = 100
BCRYPT_LENGTH = 60
EMAIL_LENGTH = 256
UUID4_LENGTH = 36


class User(Base):
    __tablename__ = "user"
    id = Column("id", String(UUID4_LENGTH), nullable=False, primary_key=True)
    username = Column("username", String(NAME_LENGTH), nullable=False)
    display_name = Column("display_name", String(NAME_LENGTH), nullable=False)

    hashed_password = Column(
        "hashed_password", String(BCRYPT_LENGTH),
        nullable=False,
    )

    tokens = relationship("SessionToken", backref="user")

    @classmethod
    def create(cls, username: str, display_name: str, raw_password: str):
        user_id = str(uuid.uuid4())

        salt = bcrypt.gensalt(rounds=12, prefix=b"2b")
        hashed_password = bcrypt.hashpw(raw_password.encode(), salt=salt)

        return cls(
            id=user_id,
            username=username,
            display_name=display_name,
            hashed_password=hashed_password.decode(),
        )

    def check_pw(self, raw_password: str) -> bool:
        hashed_password = str(self.hashed_password)
        return bcrypt.checkpw(
            raw_password.encode(),
            hashed_password.encode()
        )


class SessionToken(Base):
    __tablename__ = "session_token"

    hashed_token = Column(
        "hashed_token", String(BCRYPT_LENGTH),
        primary_key=True,
    )
    user_id = Column(String(UUID4_LENGTH), ForeignKey('user.id'))

    @staticmethod
    def issue_token(user: User) -> Tuple[Any, str]:
        randb = ""
        with open('/dev/random', 'rb') as f:
            randb = f.read(100).hex()
        token_salt = bcrypt.gensalt(rounds=12, prefix=b'2b')
        raw_token = randb + f'@{user.id}'

        hashed_token = bcrypt.hashpw(raw_token.encode(), token_salt)
        token = SessionToken(
            hashed_token=hashed_token.decode(),
            user_id=user.id,
        )
        return (token, raw_token)

    @staticmethod
    def get_userid(raw_token: str) -> Optional[str]:
        """Get userif from token
        WARNING: This method not check the validity of the token
        """
        id: Optional[str] = None
        try:
            id = raw_token.split('@')[-1]
        except (ValueError, IndexError):
            return None

        return id

    @staticmethod
    def get_token(s: scoped_session, raw_token: str) -> Optional[Any]:
        userid = SessionToken.get_userid(raw_token)
        user = s.query(User).get(userid)

        if user is None:
            return None

        for token in user.tokens:
            if token._check_token(raw_token):
                return token
        return None

    def expire(self) -> None:
        with session_scope() as s:
            s.delete(self)
            s.commit()

    def _check_token(self, raw_token: str) -> bool:
        hashed: str = str(self.hashed_token)
        return bcrypt.checkpw(
            raw_token.encode(), hashed.encode()
        )


def create_table():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    funcname = sys.argv[1]
    if funcname == "create_table":
        create_table()
