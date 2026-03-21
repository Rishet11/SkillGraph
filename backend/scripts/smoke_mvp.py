from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app


def main() -> int:
    client = TestClient(app)

    sample_resp = client.get("/samples/demo-data")
    if sample_resp.status_code != 200:
        print("FAIL: could not load demo sample")
        return 1
    sample = sample_resp.json()

    analyze_resp = client.post(
        "/analyze",
        json={
            "domain": sample["domain"],
            "resume_text": sample["resume_text"],
            "jd_text": sample["jd_text"],
        },
    )
    if analyze_resp.status_code != 200:
        print(f"FAIL: analyze returned {analyze_resp.status_code}")
        return 1

    body = analyze_resp.json()
    required_fields = ["api_version", "gap_report", "path", "reasoning", "metrics"]
    missing = [field for field in required_fields if field not in body]
    if missing:
        print(f"FAIL: missing fields {missing}")
        return 1
    if not body.get("path"):
        print("FAIL: empty learning path")
        return 1

    first_skill = body["path"][0]
    recompute_resp = client.post(
        "/recompute",
        json={
            "domain": body["domain"],
            "resume_skills": body["resume_skills"],
            "jd_data": body["jd_data"],
            "mastery_scores": body["mastery_scores"],
            "learned_skill": first_skill,
        },
    )
    if recompute_resp.status_code != 200:
        print(f"FAIL: recompute returned {recompute_resp.status_code}")
        return 1
    recompute = recompute_resp.json()
    if recompute["mastery_scores"].get(first_skill) != 1.0:
        print("FAIL: recompute did not set learned skill mastery to 1.0")
        return 1

    print("PASS: MVP smoke test completed")
    print(f"- API version: {body['api_version']}")
    print(f"- Gap count: {body['gap_count']}")
    print(f"- Path length: {len(body['path'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
