from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .analyzer import analyze_documents, run_parse, run_pathway
from .data_loader import get_demo_scenario, load_courses, load_demo_scenarios
from .graph import build_graph_payload, build_skill_graph
from .parser import parse_text_payload, parse_uploaded_file
from .schemas import (
    AnalyzeResponse,
    ParseResponse,
    PathwayRequest,
    PathwayResponse,
    RecomputeRequest,
    SampleScenario,
    SampleScenarioDetail,
    TextPayload,
)


app = FastAPI(title="SkillGraph API", version="0.2.0")

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


@app.get("/samples", response_model=list[SampleScenario])
def list_samples():
    return [
        SampleScenario(
            id=item["id"],
            label=item["label"],
            domain=item["domain"],
            story=item["story"],
        )
        for item in load_demo_scenarios()
    ]


@app.get("/samples/{sample_id}", response_model=SampleScenarioDetail)
def get_sample(sample_id: str):
    sample = get_demo_scenario(sample_id)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return SampleScenarioDetail(**sample)


@app.get("/catalog/{domain}")
def get_catalog(domain: str):
    if domain not in {"swe", "data"}:
        raise HTTPException(status_code=400, detail="Domain must be 'swe' or 'data'.")
    return load_courses(domain)  # type: ignore[arg-type]


@app.get("/graph/{domain}")
def get_graph(domain: str):
    if domain not in {"swe", "data"}:
        raise HTTPException(status_code=400, detail="Domain must be 'swe' or 'data'.")
    graph = build_skill_graph(domain)  # type: ignore[arg-type]
    zero_mastery = {node: 0.0 for node in graph.nodes}
    return build_graph_payload(graph, [], zero_mastery, set())


@app.post("/parse", response_model=ParseResponse)
async def parse_endpoint(request: Request):
    payload, resume, jd = await parse_request_to_documents(request)
    return run_parse(payload.domain, resume, jd)


@app.post("/pathway", response_model=PathwayResponse)
def pathway_endpoint(request: PathwayRequest):
    return run_pathway(request.domain, [item.model_dump() for item in request.resume_skills], request.jd_data, request.mastery_scores)


@app.post("/recompute", response_model=PathwayResponse)
def recompute_endpoint(request: RecomputeRequest):
    updated_mastery = dict(request.mastery_scores)
    updated_mastery[request.learned_skill] = 1.0
    return run_pathway(
        request.domain,
        [item.model_dump() for item in request.resume_skills],
        request.jd_data,
        updated_mastery,
    )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_endpoint(request: Request):
    payload, resume, jd = await parse_request_to_documents(request)
    return analyze_documents(payload.domain, resume, jd)


async def parse_request_to_documents(request: Request):
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = TextPayload(**(await request.json()))
        if not payload.resume_text.strip() or not payload.jd_text.strip():
            raise HTTPException(status_code=400, detail="Resume and JD text are required.")
        resume = parse_text_payload(payload.resume_text, source="text")
        jd = parse_text_payload(payload.jd_text, source="text")
        return payload, resume, jd
    if "multipart/form-data" in content_type:
        form = await request.form()
        domain = str(form.get("domain", "data")).lower()
        if domain not in {"swe", "data"}:
            raise HTTPException(status_code=400, detail="Domain must be 'swe' or 'data'.")
        payload = TextPayload(
            domain=domain,  # type: ignore[arg-type]
            resume_text=str(form.get("resume_text", "")),
            jd_text=str(form.get("jd_text", "")),
        )
        resume_file = form.get("resume_file")
        jd_file = form.get("jd_file")
        if hasattr(resume_file, "filename"):
            resume = parse_uploaded_file(
                resume_file.filename or "resume.txt",
                await resume_file.read(),
                source="upload",
            )
        elif payload.resume_text.strip():
            resume = parse_text_payload(payload.resume_text, source="text")
        else:
            raise HTTPException(status_code=400, detail="Resume content is required.")
        if hasattr(jd_file, "filename"):
            jd = parse_uploaded_file(
                jd_file.filename or "job_description.txt",
                await jd_file.read(),
                source="upload",
            )
        elif payload.jd_text.strip():
            jd = parse_text_payload(payload.jd_text, source="text")
        else:
            raise HTTPException(status_code=400, detail="Job description content is required.")
        return payload, resume, jd
    raise HTTPException(status_code=415, detail="Unsupported content type.")
