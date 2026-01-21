import requests
import time
import sys

API_URL = "http://localhost:8000/api/v1/images/process"
JOB_URL_TEMPLATE = "http://localhost:8000/api/v1/images/jobs/{}"

def verify():
    print("Submitting job...")
    try:
        response = requests.post(API_URL, json={
            "imageUrl": "https://via.placeholder.com/150",
            "transformations": ["resize:100x100", "grayscale"]
        })
        response.raise_for_status()
        data = response.json()
        job_id = data.get("jobId")
        print(f"Job submitted successfully. ID: {job_id}")
    except Exception as e:
        print(f"Failed to submit job: {e}")
        sys.exit(1)

    print("Polling for status...")
    for _ in range(10):
        time.sleep(2)
        try:
            resp = requests.get(JOB_URL_TEMPLATE.format(job_id))
            resp.raise_for_status()
            job_data = resp.json()
            status = job_data.get("status")
            print(f"Current Status: {status}")
            
            if status == "COMPLETED":
                print(f"Success! Result URL: {job_data.get('resultUrl')}")
                return
            if status == "FAILED":
                print(f"Job Failed: {job_data.get('errorMessage')}")
                sys.exit(1)
        except Exception as e:
            print(f"Error polling status: {e}")
            sys.exit(1)
    
    print("Timed out waiting for completion.")
    sys.exit(1)

if __name__ == "__main__":
    verify()
