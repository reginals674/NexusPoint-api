from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.database import get_db
from app import models, schemas
import os
import bcrypt

router = APIRouter(tags=["Auth"])

SECRET_KEY = os.environ.get("SECRET_KEY", "clave_secreta_cambiar")
ALGORITHM  = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# ─────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────

def hashear_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verificar_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

def crear_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_usuario_actual(
    token: str,
    db: Session = Depends(get_db)
) -> models.Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario: int = payload.get("sub")
        if id_usuario is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == id_usuario
    ).first()
    if usuario is None:
        raise credentials_exception
    return usuario

# ─────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────

@router.post("/login", response_model=schemas.Token)
def login(datos: schemas.LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.correo == datos.correo
    ).first()

    if not usuario or not verificar_password(datos.contrasenia, usuario.contrasenia):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    token = crear_token({"sub": str(usuario.id_usuario)})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/registro", response_model=schemas.UsuarioOut, status_code=201)
def registro(datos: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    existe = db.query(models.Usuario).filter(
        models.Usuario.correo == datos.correo
    ).first()
    if existe:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    nuevo = models.Usuario(
        matricula    = datos.matricula,
        nombre       = datos.nombre,
        apellido_p   = datos.apellido_p,
        apellido_m   = datos.apellido_m,
        correo       = datos.correo,
        contrasenia  = hashear_password(datos.contrasenia),
        cuatrimestre = datos.cuatrimestre,
        id_rol       = datos.id_rol,
        id_carrera   = datos.id_carrera,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.get("/me", response_model=schemas.UsuarioOut)
def perfil_actual(
    token: str,
    db: Session = Depends(get_db)
):
    return get_usuario_actual(token, db)