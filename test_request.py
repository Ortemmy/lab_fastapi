import requests

with open("sample.jpg", "rb") as f:
    res = requests.post("http://localhost:8000/predict", files={"file": f})
print(res.json())
