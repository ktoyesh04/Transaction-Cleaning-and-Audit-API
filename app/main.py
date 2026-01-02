from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi import Request
from app.routes.jobs import router

app = FastAPI(
	title="Transactions Cleaning API",
	description="You just need to upload a csv file we will clean it for you!",
	version="0.0.1"
)

templates = Jinja2Templates(directory=r"app\templates")


@app.get("/")
def home():
	return {"service": "Transaction Cleaning API", "status": "running"}


@app.get("/ui")
def ui_home(request: Request):
	return templates.TemplateResponse(
		"index.html",
		{"request": request}
	)
	
	
app.include_router(router)
