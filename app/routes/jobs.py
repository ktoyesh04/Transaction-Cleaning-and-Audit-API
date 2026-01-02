from fastapi import APIRouter, UploadFile, File, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
import os
import uuid
import json
import time
import pandas as pd
from app.services.processor import validate_and_clean

BASE_DIR = "data/processed"
templates = Jinja2Templates(directory=r"app\templates")
router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/upload")
def upload_csv(file: UploadFile = File(...)):
	if not file.filename.endswith(".csv"):
		raise HTTPException(status_code=400, detail="Only CSV files allowed")
	
	job_id = str(uuid.uuid4())[:8]
	
	job_folder = os.path.join(BASE_DIR, job_id)
	os.makedirs(job_folder, exist_ok=True)
	
	try:
		df = pd.read_csv(file.file)
	except Exception:
		raise HTTPException(status_code=400, detail="Invalid CSV file")
	
	cleaned_df, flagged_df, rejected_df = validate_and_clean(df)
	cleaned_df.to_csv(f"{job_folder}/cleaned.csv", index=False)
	flagged_df.to_csv(f"{job_folder}/flagged.csv", index=False)
	rejected_df.to_csv(f"{job_folder}/rejected.csv", index=False)
	
	summary = {
		"job_id": job_id,
		"total_rows": len(df),
		"cleaned": len(cleaned_df),
		"flagged": len(flagged_df),
		"rejected": len(rejected_df)
	}
	
	with open(f"{job_folder}/summary.json", "w") as f:
		json.dump(summary, f, indent=2)
	
	return {
		"summary": summary,
		"downloads": {
			"cleaned": f"/download/{job_id}/cleaned",
			"flagged": f"/download/{job_id}/flagged",
			"rejected": f"/download/{job_id}/rejected",
		}
	}


@router.post("/ui/upload")
def ui_upload(request: Request, file: UploadFile = File(...)):
	if not file.filename.endswith(".csv"):
		return templates.TemplateResponse(
			"index.html",
			{"request": request, "error": "Only CSV files allowed"}
		)
	
	job_id = str(uuid.uuid4())[:8]
	job_folder = os.path.join(BASE_DIR, job_id)
	os.makedirs(job_folder, exist_ok=True)
	
	df = pd.read_csv(file.file)
	df = df.drop_duplicates()
	
	start = time.perf_counter()
	cleaned_df, flagged_df, rejected_df = validate_and_clean(df, job_folder)
	duration = int((time.perf_counter() - start) * 1000)
	
	cleaned_df.to_csv(f"{job_folder}/cleaned.csv", index=False)
	flagged_df.to_csv(f"{job_folder}/flagged.csv", index=False)
	rejected_df.to_csv(f"{job_folder}/rejected.csv", index=False)
	
	summary = {
		"job_id": job_id,
		"total": len(df),
		"cleaned": len(cleaned_df),
		"flagged": len(flagged_df),
		"rejected": len(rejected_df),
		"processing_time_ms": duration
	}
	
	with open(f"{job_folder}/summary.json", "w") as f:
		json.dump(summary, f, indent=2)
	
	return templates.TemplateResponse(
		"index.html",
		{
			"request": request,
			"summary": summary
		}
	)


@router.get("/summary/{job_id}")
def get_summary(job_id):
	path = f"{BASE_DIR}/{job_id}/summary.json"
	if not os.path.exists(path):
		raise HTTPException(status_code=404, detail="Job not found")
	
	with open(path) as fp:
		return json.load(fp)


@router.get("/download/{job_id}/{file_type}")
def download_file(job_id, file_type):
	allowed_types = {
		"cleaned": "cleaned.csv",
		"flagged": "flagged.csv",
		"rejected": "rejected.csv"
	}
	
	if file_type not in allowed_types:
		raise HTTPException(status_code=400, detail="Invalid file type")
	
	file_path = rf"{BASE_DIR}\{job_id}\{allowed_types[file_type]}"
	
	if not os.path.exists(file_path):
		raise HTTPException(status_code=404, detail="File not found")
	
	return FileResponse(
		path=file_path,
		media_type="text/csv",
		filename=allowed_types[file_type]
	)
