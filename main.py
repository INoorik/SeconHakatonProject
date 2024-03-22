from urllib.parse import unquote

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from yandexid import *

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/login")
async def read_root(request: Request):
    code = request.query_params["code"]
    yandex_oauth = YandexOAuth(
        client_id='b8896b95d4e4486c98f09dedce538379',
        client_secret='106fbd36a6e04b4cb2eecddb2281c59c',
        redirect_uri='http://127.0.0.1:5000/login'
    )
    token = yandex_oauth.get_token_from_code(code)
    yandex_id = YandexID(token.access_token)
    js = yandex_id.get_user_info_json()
    print(js)
    return js


@app.get("/calc", response_class=HTMLResponse)
async def calc(request: Request):
    ex = " "
    try:
        ex = unquote(request.url.query)
        res = eval(ex)
    except Exception:
        return templates.TemplateResponse('main.html', {"request": request, 'req': ex, 'err': True})

    return templates.TemplateResponse("main.html", {"request": request, "req": ex, 'res': res, 'err': False})
