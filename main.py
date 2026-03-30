from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, usuarios, espacios, reservaciones, notificaciones

# Crea todas las tablas al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NexusPoint API",
    description="API REST para el sistema de reserva de espacios universitarios",
    
)
origins = [
    "http://localhost:8081",
    "http://localhost:19006",
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router,           prefix="/auth")
app.include_router(usuarios.router,       prefix="/usuarios")
app.include_router(espacios.router,       prefix="/espacios")
app.include_router(reservaciones.router,  prefix="/reservaciones")
app.include_router(notificaciones.router, prefix="/notificaciones")

@app.get("/")
def health():
    return {
        "status": "ok",
        "proyecto": "NexusPoint API",
        "docs": "/docs"
    }