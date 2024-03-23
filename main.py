from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database_api import database_connection, Task, User, Submission
from yandexid import *
import itertools
import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_user(request):
    cookie = request.cookies
    is_login = "token" in cookie
    login, email, phone, avatar, id = [""] * 5
    auth_url = "/"

    try:
        if is_login:
            access_token = cookie["token"]
            yandex_id = YandexID(access_token)
            user_data = yandex_id.get_user_info_json()
            id = user_data.id
            login = user_data.login
            email = user_data.emails[0]
            phone = user_data.default_phone.number
            avatar = user_data.default_avatar_id
            if User(id, '', 0).is_exist(database_connection):
                login = User.pull_from_database(database_connection, id).name
            else:
                is_login = False

    except Exception:
        is_login = False

    if not is_login:
        yandex_oauth = YandexOAuth(
            client_id='b8896b95d4e4486c98f09dedce538379',
            client_secret='106fbd36a6e04b4cb2eecddb2281c59c',
            redirect_uri='http://127.0.0.1:5000/set_token'
        )
        auth_url = yandex_oauth.get_authorization_url()

    return {"request": request, "login_name": login, "is_login": is_login,
            "login_ref": auth_url, "email": email, "phone": phone, "avatar": avatar, "id": id}


@app.get("/")
async def main_page(request: Request):
    params = get_user(request)
    params["rating"] = User.pull_from_database(database_connection, params["id"]).rating
    params["current"] = "Home"
    return templates.TemplateResponse("html/main.html", params)


@app.get("/users/{id}")
async def main_page(id, request: Request):
    params = get_user(request)
    print(params["id"])
    print(id)
    if str(id) == str(params["id"]):
        return RedirectResponse("/")

    params["rating"] = User.pull_from_database(database_connection, id).rating
    params["current"] = "Not Home"
    return templates.TemplateResponse("html/main.html", params)


@app.get("/logout")
async def logout():
    response = RedirectResponse("/")
    response.delete_cookie("token")
    return response


@app.get("/set_token")
async def set_token(response: Response, request: Request):
    code = request.query_params["code"]
    yandex_oauth = YandexOAuth(
        client_id='b8896b95d4e4486c98f09dedce538379',
        client_secret='106fbd36a6e04b4cb2eecddb2281c59c',
        redirect_uri='http://127.0.0.1:5000/set_token'
    )
    token = yandex_oauth.get_token_from_code(code)
    response = RedirectResponse("/login")
    response.set_cookie(key="token", value=token.access_token)
    return response


@app.get("/login")
async def login(response: Response, request: Request):
    params = get_user(request)
    user = User(params["id"], "", 0)
    if user.is_exist(database_connection):
        response = RedirectResponse("/")
    else:
        response = RedirectResponse("/register")

    return response


@app.get("/top")
async def top(request: Request):
    params = get_user(request)
    users = list(User.get_top(database_connection, 10))
    params["users"] = users
    params["current"] = "Top"
    return templates.TemplateResponse("html/top.html", params)


@app.get("/register")
async def register(request: Request):
    params = get_user(request)
    params["current"] = "Home"
    return templates.TemplateResponse("html/register.html", params)


@app.get("/save_user")
async def save_user(request: Request):
    params = get_user(request)
    user_login = request.query_params["login"]
    user = User(params["id"], user_login, 0)
    if not user.is_exist(database_connection):
        user.flush(database_connection)

    return RedirectResponse("/")


@app.get("/archive")
async def archive(request: Request):
    params = get_user(request)
    params["current"] = "Tasks"
    params["tasks"] = list(itertools.islice(Task.get_all(database_connection), 5))

    return templates.TemplateResponse("html/archive.html", params)


@app.get("/tasks/{task_id}")
async def task(request: Request, task_id):
    params = get_user(request)
    try:
        task = Task.pull_from_database(database_connection, task_id)
        params["current"] = "Tasks"
        params["task"] = task
        params["submissions"] = Submission.get_by_user_and_task(database_connection, params["id"], task.id, 10)
        return templates.TemplateResponse("html/task.html", params)
    except Exception:
        return RedirectResponse("/archive")


@app.get("/submit_solution/{task_id}")
async def submit_solution(request: Request, task_id):
    params = get_user(request)
    try:
        task = Task.pull_from_database(database_connection, task_id)
        user_id = params["id"]
        user_answer = request.query_params["answer"]
        true_answer = task.answer_key
        verdict = "Accepted" if user_answer == true_answer else "Wrong answer"
        submission = Submission(user_id, task_id, verdict, datetime.datetime.now(), user_answer)
        submission.flush(database_connection)
        return RedirectResponse(f"/tasks/{task_id}")
    except Exception:
        return RedirectResponse("/archive")


app.mount("/css", StaticFiles(directory="templates/css"), "css")