import uvicorn
from backend.main import app  # ajusta o import conforme tua estrutura

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
