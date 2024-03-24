from fastapi import FastAPI, Request, Response, UploadFile, Form
from typing_extensions import Annotated
from typing import Optional
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
    permission = 0
    login, email, phone, avatar, id = [""] * 5
    auth_url = "/"
    color = "silver"

    try:
        if is_login:
            access_token = cookie["token"]
            yandex_id = YandexID(access_token)
            user_data = yandex_id.get_user_info_json()
            id = user_data.id
            login = user_data.login
            email = user_data.emails[0]
            phone = user_data.default_phone.number
            avatar = "https://avatars.yandex.net/get-yapic/" + user_data.default_avatar_id + "/islands-200"
            user = User(id, '', 0, "", "")
            if user.is_exist(database_connection):
                user = User.pull_from_database(database_connection, id)
                login = user.name
                permission = User.get_permission(id, database_connection)
                color = user.color_by_rating(user.rating)
            else:
                is_login = False

    except Exception:
        is_login = False

    if not is_login:
        yandex_oauth = YandexOAuth(
            client_id='b8896b95d4e4486c98f09dedce538379',
            client_secret='106fbd36a6e04b4cb2eecddb2281c59c',
            redirect_uri='http://www.seconhakatonctfproject.fun/set_token'
        )
        auth_url = yandex_oauth.get_authorization_url()

    return {"request": request, "login_name": login, "is_login": is_login, "permission": permission,
            "login_ref": auth_url, "email": email, "phone": phone, "avatar": avatar, "id": id, "color": color}


@app.get("/")
async def main_page(request: Request):
    params = get_user(request)
    user = User(params["id"], "", 0, "", "")
    if user.is_exist(database_connection):
        user = User.pull_from_database(database_connection, params["id"])
        params["show"] = True
        params["rating"] = user.rating
        params["name"] = params["login_name"]
        submissions = list(user.get_submissions(database_connection, 10))
        tasks = [Task.pull_from_database(database_connection, submission.task_id) for submission in submissions]
        params["tasks_and_submissions"] = list(zip(tasks, submissions))
    else:
        params["show"] = False

    params["user_color"] = params["color"]
    params["current"] = "Home"
    return templates.TemplateResponse("html/main.html", params)


@app.get("/users/{id}")
async def users(id, request: Request):
    params = get_user(request)
    if (str(id) == str(params["id"]) or
            not User(id, "", 0, "", "").is_exist(database_connection)):
        return RedirectResponse("/")

    user = User.pull_from_database(database_connection, id)
    params["show"] = True
    params["rating"] = user.rating
    params["name"] = user.name
    params["avatar"] = user.avatar
    params["user_color"] = user.color_by_rating(user.rating)
    params["current"] = "Not Home"
    submissions = list(user.get_submissions(database_connection, 10))
    tasks = [Task.pull_from_database(database_connection, submission.task_id) for submission in submissions]
    params["tasks_and_submissions"] = list(zip(tasks, submissions))
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
        redirect_uri='http://www.seconhakatonctfproject.fun/set_token'
    )
    token = yandex_oauth.get_token_from_code(code)
    response = RedirectResponse("/login")
    response.set_cookie(key="token", value=token.access_token)
    return response


@app.get("/login")
async def login(response: Response, request: Request):
    params = get_user(request)
    user = User(params["id"], "", 0, "", "")
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
    user = User(params["id"], user_login, 0, params["email"], params["avatar"])
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
        old_submissions = list(Submission.get_by_user_and_task(database_connection, user_id, task_id))
        is_solved = any(submission.verdict == "Accepted" for submission in old_submissions)
        user_answer = request.query_params["answer"]
        true_answer = task.answer_key
        verdict = "Accepted" if user_answer == true_answer else "Wrong answer"
        submission = Submission(user_id, task_id, verdict, datetime.datetime.now(), user_answer)
        submission.flush(database_connection)
        if is_solved or verdict != "Accepted":
            return RedirectResponse(f"/tasks/{task_id}")
        user = User.pull_from_database(database_connection, user_id)
        user.update_rating(task.difficulty)
        user.flush(database_connection)
        return RedirectResponse(f"/tasks/{task_id}")
    except Exception:
        return RedirectResponse("/archive")


@app.get("/submissions/{task_id}")
async def submissions(request: Request, task_id):
    try:
        task = Task.pull_from_database(database_connection, task_id)
        params = get_user(request)
        submissions = list(task.get_submissions(database_connection, 10))
        users = [User.pull_from_database(database_connection, sub.user_id) for sub in submissions]
        params["users_and_submissions"] = list(zip(users, submissions))
        params["task_id"] = task.id
        return templates.TemplateResponse("html/submissions.html", params)
    except Exception:
        return RedirectResponse("/")


@app.get("/moder_panel")
async def moder_panel(request: Request):
    params = get_user(request)
    if params["permission"] == 0:
        return RedirectResponse("/")

    params["current"] = "Model panel"
    return templates.TemplateResponse("html/moder_panel.html", params)


@app.get("/admin_panel")
async def admin_panel(request: Request):
    params = get_user(request)
    if params["permission"] < 2:
        return RedirectResponse("/")

    params["current"] = "Admin panel"
    params["users"] = list(map(lambda x: [x, User.get_permission(x.id, database_connection)],
                               User.get_top(database_connection)))
    return templates.TemplateResponse("html/admin_panel.html", params)


@app.post("/permission_edit/{id}")
async def permission_edit(request: Request, id, permission_level: Optional[int] = Form(None)):
    params = get_user(request)
    if params["permission"] < 2:
        return RedirectResponse("/")

    print(id, permission_level)
    User(id, "", 0, "", "").set_permission(permission_level, database_connection)
    return RedirectResponse("/admin_panel", status_code=303)


@app.post("/add_task")
async def add_task(request: Request, name: Optional[str] = Form(None), description: Optional[str] = Form(None),
                   difficulty: Optional[int] = Form(None), answer_key: Optional[str] = Form(None),
                   file: UploadFile = None):
    params = get_user(request)
    if params["permission"] == 0:
        return RedirectResponse("/")

    if name is None or description is None or difficulty is None or answer_key is None:
        return RedirectResponse("/moder_panel", status_code=303)

    if file.filename:
        up_file = open("task_files/" + file.filename, "wb")
        up_file.write(file.file.read())
        file.file.close()
        up_file.close()

    Task(0, name, description, difficulty, answer_key, file.filename).flush(database_connection)

    return RedirectResponse("/archive", status_code=303)


app.mount("/css", StaticFiles(directory="templates/css"), "css")
app.mount("/task_files", StaticFiles(directory="task_files"), "task_files")
