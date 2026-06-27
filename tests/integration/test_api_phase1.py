from fastapi.testclient import TestClient

from meeting_intel.api.app import create_app


def test_upload_summarize_and_ask_offline():
    client = TestClient(create_app())
    transcript = "Asha: We need the demo ready by Friday.\nRahul: I will finish the API."

    upload_response = client.post(
        "/upload",
        json={"title": "Demo", "text": transcript, "participants": ["Asha", "Rahul"]},
    )
    assert upload_response.status_code == 200
    meeting_id = upload_response.json()["meeting"]["meeting_id"]

    summarize_response = client.post("/summarize", json={"meeting_id": meeting_id})
    assert summarize_response.status_code == 200
    assert summarize_response.json()["meeting"]["summary"].startswith("Offline summary")

    ask_response = client.post(
        "/ask",
        json={"meeting_id": meeting_id, "question": "Who will finish the API?", "top_k": 3},
    )
    assert ask_response.status_code == 200
    assert "sources" in ask_response.json()
