from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_text_analysis():
    response = client.post(
        "/analyze",
        json={
            "resume_text": "Python SQL Tableau statistics dashboards machine learning",
            "job_description_text": (
                "Required skills: Python, SQL, statistics. "
                "Preferred: Tableau, data visualization. Bonus: machine learning."
            ),
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "fit_score" in body
    assert body["fit_score"] >= 50
    assert len(body["resume_skills"]) >= 3
    assert len(body["target_skills"]) >= 3


def test_missing_input_rejected():
    response = client.post("/analyze", json={"resume_text": "", "job_description_text": ""})
    assert response.status_code == 400


def test_samples():
    response = client.get("/samples")
    assert response.status_code == 200
    assert len(response.json()) >= 2

