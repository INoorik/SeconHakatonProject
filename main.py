import token
from urllib.parse import unquote

from fastapi import FastAPI, Request, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from yandexid import *

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def main_page(response: Response, request: Request):
    cookie = request.cookies
    is_login = "token" in cookie
    login = ""
    auth_url = "/"

    try:
        if is_login:
            access_token = cookie["token"]
            yandex_id = YandexID(access_token)
            js = yandex_id.get_user_info_json()
            login = js.login
    except Exception:
        is_login = False

    if not is_login:
        yandex_oauth = YandexOAuth(
            client_id='b8896b95d4e4486c98f09dedce538379',
            client_secret='106fbd36a6e04b4cb2eecddb2281c59c',
            redirect_uri='http://127.0.0.1:5000/login'
        )
        auth_url = yandex_oauth.get_authorization_url()

    return templates.TemplateResponse("html/main.html", {"request": request, "is_login": is_login,
                                                         "login_name": login, "login_ref": auth_url})


@app.get("/logout")
async def logout(response: Response, request: Request):
    response = RedirectResponse("/")
    response.delete_cookie("token")
    return response


@app.get("/login")
async def login(response: Response, request: Request):
    code = request.query_params["code"]
    yandex_oauth = YandexOAuth(
        client_id='b8896b95d4e4486c98f09dedce538379',
        client_secret='106fbd36a6e04b4cb2eecddb2281c59c',
        redirect_uri='http://127.0.0.1:5000/login'
    )
    token = yandex_oauth.get_token_from_code(code)
    response = RedirectResponse("/")
    response.set_cookie(key="token", value=token.access_token)
    return response
