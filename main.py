from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
import sqlite3
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).parent
templates_dir = BASE_DIR / "templates"
static_dir = BASE_DIR / "static"

# Static files and templates
app.mount("/static", StaticFiles(directory=static_dir), name="static")
env = Environment(loader=FileSystemLoader(str(templates_dir)))

# DB setup
DB_PATH = BASE_DIR / "tornado.db"
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS names (id INTEGER PRIMARY KEY, name TEXT)")

init_db()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    with sqlite3.connect(DB_PATH) as conn:
        names = [row[0] for row in conn.execute("SELECT name FROM names ORDER BY id DESC LIMIT 5")]
    template = env.get_template("index.html")
    return template.render(names=names, request=request)

@app.post("/submit", response_class=HTMLResponse)
async def submit_name(name: str = Form(...)):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO names (name) VALUES (?)", (name,))
    return RedirectResponse("/", status_code=303)
