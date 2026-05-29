from sqlalchemy.orm import DeclarativeBase , Mapped , mapped_column
class Base (DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str]
    password: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=False)
class Film(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    avt: Mapped[str]
    janr: Mapped[str]


class SessionID(Base) :
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(primary_key=True,autoincrement=False)
    user_id: Mapped[int]
