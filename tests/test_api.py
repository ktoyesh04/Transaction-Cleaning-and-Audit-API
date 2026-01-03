from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)


def test_csv_upload_endpoint():
    csv_content = """account_id,amount,date,customer_name
1,1.5L,01/01/2024,Amit
2,-500,01/01/2024,Ravi
"""

    response = client.post(
        "/jobs/upload",
        files={
            "file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert "summary" in data
    assert data["summary"]["flagged"] == 1
    assert data["summary"]["rejected"] == 1
