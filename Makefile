.PHONY: test eval run-backend run-frontend install demo

install:
	cd backend && uv pip install -r requirements.txt --python .venv/Scripts/python.exe
	cd frontend && cmd.exe /c npm install

test:
	cd backend && .venv/Scripts/pytest -v

eval:
	cd backend && .venv/Scripts/python run_eval.py

run-backend:
	cd backend && .venv/Scripts/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && cmd.exe /c npm run dev

demo:
	cd backend && .venv/Scripts/python run_eval.py
