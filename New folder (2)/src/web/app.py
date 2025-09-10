from __future__ import annotations

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio

from src.weather_graph.live import fetch_current_weather


app = FastAPI(title="Weather Report")
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/report", response_class=HTMLResponse)
async def report(request: Request, location: str = Form(...)):
    data = await fetch_current_weather(location)
    return templates.TemplateResponse("report.html", {"request": request, "data": data, "location": location})



