from urllib.parse import unquote

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/calc", response_class=HTMLResponse)
def calc(request: Request):
    ex = " "
    try:
        ex = unquote(request.url.query)
        res = eval(ex)
    except Exception:
        return templates.TemplateResponse('main.html', {"request": request, 'req': ex, 'err': True})

    return templates.TemplateResponse("main.html", {"request": request, "req": ex, 'res': res, 'err': False})
