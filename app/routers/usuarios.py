from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.routers.auth import hashear_password

router = APIRouter(tags=["Usuarios"])

# ─────────────────────────────────────────
# LISTAR TODOS
# ─────────────────────────────────────────

@router.get("/", response_model=list[schemas.UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()


# ─────────────────────────────────────────
# OBTENER UNO
# ─────────────────────────────────────────

@router.get("/{id_usuario}", response_model=schemas.UsuarioOut)
def obtener_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == id_usuario
    ).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


# ─────────────────────────────────────────
# CREAR
# ─────────────────────────────────────────

@router.post("/", response_model=schemas.UsuarioOut, status_code=201)
def crear_usuario(datos: schemas.UsuarioCreate, db: Session = Depends(get_db)):
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


# ─────────────────────────────────────────
# ACTUALIZAR
# ─────────────────────────────────────────

@router.put("/{id_usuario}", response_model=schemas.UsuarioOut)
def actualizar_usuario(
    id_usuario: int,
    datos: schemas.UsuarioUpdate,
    db: Session = Depends(get_db)
):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == id_usuario
    ).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario


# ─────────────────────────────────────────
# ELIMINAR
# ─────────────────────────────────────────

@router.delete("/{id_usuario}", status_code=204)
def eliminar_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == id_usuario
    ).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(usuario)
    db.commit()


# ─────────────────────────────────────────
# LISTAR ROLES Y CARRERAS (catálogos)
# ─────────────────────────────────────────

@router.get("/catalogos/roles", response_model=list[schemas.RolOut])
def listar_roles(db: Session = Depends(get_db)):
    return db.query(models.Rol).all()


@router.get("/catalogos/carreras", response_model=list[schemas.CarreraOut])
def listar_carreras(db: Session = Depends(get_db)):
    return db.query(models.Carrera).all()