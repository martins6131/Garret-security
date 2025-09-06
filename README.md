🔐 Security System Dashboard

A smart security system built with FastAPI, React + Tailwind, MQTT, and PostgreSQL.
It provides real-time monitoring, motion alerts, and system controls via a modern dashboard UI.

✨ Features

✅ User Authentication (JWT, roles: admin, guest)

✅ Arm/Disarm System via dashboard

✅ Real-time Alerts from sensors (MQTT → WebSocket)

✅ Live Status Badge (armed/disarmed indicator)

✅ Event Logs stored in PostgreSQL

✅ Simulator for fake motion events

🖼️ Dashboard Preview

Example UI styled with Tailwind + Framer Motion

📂 Project Structure
security-system/
├── backend/      # FastAPI + MQTT + PostgreSQL
├── frontend/     # React + Tailwind + Framer Motion
├── simulator/    # Fake motion sensor events
└── README.md

🚀 Getting Started
1️⃣ Backend (FastAPI + PostgreSQL + MQTT)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

2️⃣ Frontend (React + Tailwind + Framer Motion)
cd frontend
npm install
npm start

3️⃣ Simulator (Fake Motion Sensor)
cd simulator
python motion_sim.py

⚡ Tech Stack

Backend → FastAPI, SQLAlchemy, PostgreSQL, JWT Auth

Frontend → React, TailwindCSS, Framer Motion

Messaging → MQTT (paho-mqtt)

Database → PostgreSQL

🛠️ Environment Variables

Create a .env file in backend/ based on .env.example:

DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=super_secret

📜 License

MIT © 2025
