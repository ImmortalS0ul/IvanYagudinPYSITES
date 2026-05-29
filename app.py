from typing import Annotated

from fastapi import FastAPI, Form, Request,Cookie, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from model import Base,Film,User,SessionID
from hashlib import sha256
from uuid import uuid4
import uvicorn

app = FastAPI()
html = Jinja2Templates(directory="html")


engine = create_engine("sqlite:///database.db")
Base.metadata.create_all(engine)

@app.get("/")
def index(request: Request,
          session_id:Annotated[str | None, Cookie()] = None):
    with Session(engine) as session:
        user = None
        if session_id:
            session_id = session.get(SessionID,session_id)
            if session_id :
                user = session.get(User,session_id.user_id)
        data = session.scalars(select(Film)).all()
        return html.TemplateResponse(request, "index.html", {"films": data , "user" : user})
@app.get("/login_form")
def index(request: Request):
    return html.TemplateResponse(request, "login.html")

@app.get("/reg_form")
def index(request: Request):
    return html.TemplateResponse(request, "Reg.html")

@app.get("/add_form")
def index(request: Request):
    return html.TemplateResponse(request, "add.html")

@app.post("/add")
def add(
        title: Annotated[str, Form()],
        janr: Annotated[str, Form()],
        avt: Annotated[str, Form()],
        session_id: Annotated[str,Cookie()] = None

):
    if not session_id:
        return " войдите"
    with Session(engine) as session:
        session_id = session.get(SessionID, session_id)
        if not session_id:
            return "войдите"
        session.add(Film (
            name=title,
            janr=janr,
            avt=avt,
        ))
        session.commit()
    return RedirectResponse("/",status_code=302)
@app.post("/reg")
def reg(
    login: Annotated[str, Form()],
    password: Annotated[str, Form()],
    password2: Annotated[str, Form()]
):
    if password != password2:
        return "Пароли не совпадают"
    with Session(engine) as session:
        if session.scalars(select(User).where(User.login == login)).one_or_none():
            return "Такой пользователь уже есть"
        password = sha256(password.encode("utf_8")).hexdigest()
        session.add(User(login=login,password=password))
        session.commit()
    return RedirectResponse("/login_form",status_code=302)
@app.post("/login")
def login(
    login: Annotated[str, Form()],
    password: Annotated[str, Form()]
):
    with Session(engine) as session:
        user = session.scalars(select(User).where(User.login == login)).one_or_none( )
        if not user:
            return "такого нет"
        password = sha256(password.encode("utf-8")).hexdigest()
        if user.password != password:
            return "Пароль не верный "
        session_id = str(uuid4())
        session.add(SessionID(id=session_id,user_id=user.id))
        session.commit()
        response = RedirectResponse("/",status_code=302)
        response.set_cookie("session_id",session_id)
        return response
    pass
@app.get("/delete/{id}")
def delete(
        id:int,
        session_id: Annotated[str,Cookie()] = None
):
    if session_id is None:
        return"Войдите"
    with Session(engine) as session:
        session_id = session.get(SessionID, session_id)
        if not session_id:
            return "войдите"
        user = session.get(User,session_id.user_id)
        if not user.is_admin:
            return "только админ"
        session.delete(session.get(Film,id))
        session.commit()
    return RedirectResponse("/",status_code=302)


    with Session(engine) as session:
        user = session.get(Film, id)
        session.delete(user)
        session.commit()
    return RedirectResponse("/", status_code=302)

@app.get("/set_/{login}")
def set_admin(login : str):
    with Session(engine) as session:
        user = session.scalars(select(User).where(User.login == login)).one_or_none( )
        user.is_admin = True
        session.add(user)
        session.commit()
    return RedirectResponse("/" , status_code=302)

@app.get("/film/{id}")
def filminfo(
        request:Request,
        id:int,
        session_id:Annotated[str,Cookie()] = None
):
    if not session_id:
        return " Войдите"
    with Session(engine) as session:
        session_id = session.get(SessionID, session_id)
        if not session_id:
            return"Войдите"
        user = session.get(User, session_id.user_id)
        film = session.get(Film,id)
        return html.TemplateResponse(request,"films.html",{"films" : film,"is_admin":user.is_admin})


@app.get("/logout")
def logout(
        response: Response,
        session_id: Annotated[str | None, Cookie()] = None
):
    if session_id:
        with Session(engine) as session:
            # Удаляем запись о сессии из базы данных
            session_to_delete = session.get(SessionID, session_id)
            if session_to_delete:
                session.delete(session_to_delete)
                session.commit()

    # Создаём ответ с редиректом и удаляем cookie
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("session_id")
    return response

if __name__ == "__main__":
    uvicorn.run(app)