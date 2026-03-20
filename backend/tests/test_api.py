from fastapi.testclient import TestClient

from app.main import app
from app import skills as skills_module


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_samples_return_two_fixed_demos():
    response = client.get("/samples")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {item["domain"] for item in body} == {"swe", "data"}


def test_parse_and_pathway_are_deterministic_for_data_demo():
    sample = client.get("/samples/demo-data").json()
    parse_payload = {
        "domain": sample["domain"],
        "resume_text": sample["resume_text"],
        "jd_text": sample["jd_text"],
    }
    parsed_once = client.post("/parse", json=parse_payload)
    parsed_twice = client.post("/parse", json=parse_payload)
    assert parsed_once.status_code == 200
    assert parsed_once.json() == parsed_twice.json()

    pathway_input = parsed_once.json()
    pathway_once = client.post("/pathway", json=pathway_input)
    pathway_twice = client.post("/pathway", json=pathway_input)
    assert pathway_once.status_code == 200
    assert pathway_once.json() == pathway_twice.json()


def test_swe_path_respects_expected_start():
    sample = client.get("/samples/demo-swe").json()
    response = client.post(
        "/analyze",
        json={
            "domain": sample["domain"],
            "resume_text": sample["resume_text"],
            "jd_text": sample["jd_text"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["domain"] == "swe"
    assert body["gap_count"] >= 4
    path = body["path"]
    assert "Testing" in path
    assert "Docker" in path
    assert "Linux/CLI" in path
    assert "System Design" in path
    assert "Microservices" in path
    assert path.index("Linux/CLI") < path.index("Docker")
    assert path.index("System Design") < path.index("Microservices")


def test_recompute_marks_skill_as_learned():
    sample = client.get("/samples/demo-data").json()
    parsed = client.post(
        "/parse",
        json={
            "domain": sample["domain"],
            "resume_text": sample["resume_text"],
            "jd_text": sample["jd_text"],
        },
    ).json()
    pathway = client.post("/pathway", json=parsed).json()
    learned_skill = pathway["path"][0]
    response = client.post(
        "/recompute",
        json={
            "domain": sample["domain"],
            "resume_skills": parsed["resume_skills"],
            "jd_data": parsed["jd_data"],
            "mastery_scores": pathway["mastery_scores"],
            "learned_skill": learned_skill,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["mastery_scores"][learned_skill] == 1.0
    assert learned_skill not in body["path"]


def test_catalogs_are_domain_bounded():
    swe_catalog = client.get("/catalog/swe")
    data_catalog = client.get("/catalog/data")
    assert swe_catalog.status_code == 200
    assert data_catalog.status_code == 200
    assert all(item["domain"] in {"SWE", "SWE/Data"} for item in swe_catalog.json())
    assert all(item["domain"] in {"Data", "SWE/Data"} for item in data_catalog.json())


def test_graph_endpoint_returns_domain_graph():
    response = client.get("/graph/data")
    assert response.status_code == 200
    body = response.json()
    assert body["nodes"]
    assert body["edges"]


def test_gemini_classifier_result_is_filtered_to_taxonomy(monkeypatch):
    monkeypatch.setattr(
        skills_module,
        "classify_with_gemini",
        lambda *_args, **_kwargs: [
            {"skill": "Python", "mentions": 2, "in_recent_experience": True},
            {"skill": "Invented Skill", "mentions": 99, "in_recent_experience": True},
        ],
    )
    result = skills_module.classify_resume_skills("Python and something else", "data")
    assert result == [{"skill": "Python", "mentions": 2, "in_recent_experience": True}]


def test_gemini_jd_classifier_result_is_filtered_to_taxonomy(monkeypatch):
    monkeypatch.setattr(
        skills_module,
        "classify_with_gemini",
        lambda *_args, **_kwargs: {
            "required": ["Machine Learning Fundamentals", "Invented Skill"],
            "preferred": ["NLP", "Another Fake Skill"],
        },
    )
    jd = skills_module.classify_jd("ignored", "data")
    assert jd.required == ["Machine Learning Fundamentals"]
    assert jd.preferred == ["NLP"]
