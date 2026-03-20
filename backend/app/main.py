from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .analyzer import analyze_documents
from .data_loader import load_samples
from .parser import parse_text_payload, parse_uploaded_file
from .schemas import AnalyzeResponse, SampleContent, SampleItem, TextPayload


app = FastAPI(title="SkillGraph API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/samples", response_model=list[SampleItem])
def list_samples():
    return [
        SampleItem(id=sample["id"], label=sample["label"], type=sample["type"])
        for sample in load_samples()
    ]


@app.get("/samples/{sample_id}", response_model=SampleContent)
def get_sample(sample_id: str):
    for sample in load_samples():
        if sample["id"] == sample_id:
            return SampleContent(**sample)
    raise HTTPException(status_code=404, detail="Sample not found")


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: Request):
    try:
        content_type = request.headers.get("content-type", "")
        payload = None
        resume_file: UploadFile | None = None
        job_description_file: UploadFile | None = None

        if "application/json" in content_type:
            payload = TextPayload(**(await request.json()))
        elif "multipart/form-data" in content_type:
            form = await request.form()
            resume_file = form.get("resume_file")
            job_description_file = form.get("job_description_file")
            payload = TextPayload(
                resume_text=str(form.get("resume_text", "")),
                job_description_text=str(form.get("job_description_text", "")),
            )
        else:
            raise HTTPException(status_code=415, detail="Unsupported content type.")

        if resume_file:
            resume = parse_uploaded_file(
                resume_file.filename or "resume.txt",
                await resume_file.read(),
                source="upload",
            )
        else:
            text = payload.resume_text if payload else ""
            if not text.strip():
                raise HTTPException(status_code=400, detail="Resume content is required.")
            resume = parse_text_payload(text, source="text")

        if job_description_file:
            job_description = parse_uploaded_file(
                job_description_file.filename or "job_description.txt",
                await job_description_file.read(),
                source="upload",
            )
        else:
            text = payload.job_description_text if payload else ""
            if not text.strip():
                raise HTTPException(status_code=400, detail="Job description content is required.")
            job_description = parse_text_payload(text, source="text")

        return analyze_documents(resume, job_description)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
