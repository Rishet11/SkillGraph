import requests
import json
import os

def test_universal_engine():
    url = "http://127.0.0.1:8000/analyze"
    
    # Load sample nurse files
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    with open(os.path.join(root, 'data', 'samples', 'sample_resume_nurse.txt')) as f:
        resume_text = f.read()
    with open(os.path.join(root, 'data', 'samples', 'sample_jd_nurse.txt')) as f:
        jd_text = f.read()
        
    payload = {
        "resume_text": resume_text,
        "jd_text": jd_text,
        "domain": None # Trigger Auto-Detection
    }
    
    print("Sending 'Universal' Request (Healthcare Scenario)...")
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS!")
            print(f"Detected Domain: {data['domain']}")
            print(f"Industry Headline: {data['summary']['headline']}")
            print(f"Gap Count: {data['gap_count']}")
            print(f"Sample Gap: {data['gap_skills'][0] if data['gap_skills'] else 'None'}")
            
            # Check for Custom Course
            if data['path']:
                first_skill = data['path'][0]
                course = data['course_map'].get(first_skill)
                print(f"Course for {first_skill}: {course['name']} ({course['id']})")
        else:
            print(f"FAILED: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_universal_engine()
