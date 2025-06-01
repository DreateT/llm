# llm

#Step1: Launch (local)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

#Step2: Username and Password are hardcoded.
#Use curl to login and grab the auth code
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin", "password":"password123"}'

#Step3: Run Query as below
curl -X POST http://localhost:8000/chat -H "Authorization: Bearer <Paste Auth Code from Step 2>" -H "Content-Type: application/json" -d '{"query":"Did any SRM T3 exceed 33 °C battery temperature in the last 24 h?"}'
