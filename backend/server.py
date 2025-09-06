from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import jwt, bcrypt
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
import os

# Config
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# DB Setup
ENGINE = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=ENGINE)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    hashed_pin = Column(String)
    role = Column(String)  # 'admin', 'guest'

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    time = Column(DateTime, server_default=func.now())
    event = Column(String)

Base.metadata.create_all(ENGINE)

# Models
class Login(BaseModel):
    username: str
    pin: str

class Alert(BaseModel):
    message: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(db: Session, username: str, pin: str):
    user = db.query(User).filter(User.username == username).first()
    if user and bcrypt.checkpw(pin.encode(), user.hashed_pin.encode()):
        return user
    return None

def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def add_log(db: Session, event: str):
    db.add(Log(event=event))
    db.commit()

# FastAPI app
app = FastAPI()

# MQTT Setup
mqtt_client = mqtt.Client()

def on_message(client, userdata, msg):
    db = SessionLocal()
    payload = msg.payload.decode()
    event = f"[MQTT] {msg.topic}: {payload}"
    print(event)
    add_log(db, event)
    db.close()

@app.on_event("startup")
def start_mqtt():
    mqtt_client.on_message = on_message
    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.subscribe("/sensors/#")
    mqtt_client.loop_start()

@app.on_event("shutdown")
def stop_mqtt():
    mqtt_client.loop_stop()

@app.post("/login")
def login(login: Login, db: Session = Depends(get_db)):
    user = authenticate_user(db, login.username, login.pin)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/unlock")
def unlock(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(403, "Insufficient permissions")
        mqtt_client.publish("/devices/lock", "unlock")
        add_log(db, f"Lock unlocked by {payload['sub']}")
        return {"status": "unlocked"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

@app.post("/alert")
def send_alert(alert: Alert, db: Session = Depends(get_db)):
    print(f"🚨 Alert sent: {alert.message}")
    add_log(db, f"ALERT: {alert.message}")
    return {"status": "alerted"}

@app.get("/api/logs")
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(Log).order_by(Log.time.desc()).limit(50).all()
    return [{"id": l.id, "time": l.time, "event": l.event} for l in logs]

@app.post("/api/arm")
def arm_system(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        mqtt_client.publish("/devices/lock", "arm")
        add_log(db, f"System armed by {payload['sub']}")
        return {"status": "armed"}
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

@app.post("/api/disarm")
def disarm_system(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        mqtt_client.publish("/devices/lock", "disarm")
        add_log(db, f"System disarmed by {payload['sub']}")
        return {"status": "disarmed"}
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
