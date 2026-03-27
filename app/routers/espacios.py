from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(tags=["Espacios"])

# ─────────────────────────────────────────
# LISTAR TODOS
# ─────────────────────────────────────────

@router.get("/", response_model=list[schemas.EspacioOut])
def listar_espacios(db: Session = Depends(get_db)):
    return db.query(models.Espacio).all()


# ─────────────────────────────────────────
# FILTRAR POR TIPO
# ─────────────────────────────────────────

@router.get("/tipo/{id_tipo}", response_model=list[schemas.EspacioOut])
def espacios_por_tipo(id_tipo: int, db: Session = Depends(get_db)):
    return db.query(models.Espacio).filter(
        models.Espacio.id_tipo_espacio == id_tipo
    ).all()


# ─────────────────────────────────────────
# FILTRAR POR ESTADO
# ─────────────────────────────────────────

@router.get("/estado/{id_estado}", response_model=list[schemas.EspacioOut])
def espacios_por_estado(id_estado: int, db: Session = Depends(get_db)):
    return db.query(models.Espacio).filter(
        models.Espacio.id_estado_espacio == id_estado
    ).all()


# ─────────────────────────────────────────
# OBTENER UNO
# ─────────────────────────────────────────

@router.get("/{id_espacio}", response_model=schemas.EspacioOut)
def obtener_espacio(id_espacio: int, db: Session = Depends(get_db)):
    espacio = db.query(models.Espacio).filter(
        models.Espacio.id_espacio == id_espacio
    ).first()
    if not espacio:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    return espacio


# ─────────────────────────────────────────
# CREAR
# ─────────────────────────────────────────

@router.post("/", response_model=schemas.EspacioOut, status_code=201)
def crear_espacio(datos: schemas.EspacioCreate, db: Session = Depends(get_db)):
    existe = db.query(models.Espacio).filter(
        models.Espacio.codigo_espacio == datos.codigo_espacio
    ).first()
    if existe:
        raise HTTPException(status_code=400, detail="Ya existe un espacio con ese código")

    nuevo = models.Espacio(
        codigo_espacio      = datos.codigo_espacio,
        nombre_espacio      = datos.nombre_espacio,
        descripcion_espacio = datos.descripcion_espacio,
        capacidad           = datos.capacidad,
        id_tipo_espacio     = datos.id_tipo_espacio,
        id_estado_espacio   = datos.id_estado_espacio,
        id_piso             = datos.id_piso,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# ─────────────────────────────────────────
# ACTUALIZAR
# ─────────────────────────────────────────

@router.put("/{id_espacio}", response_model=schemas.EspacioOut)
def actualizar_espacio(
    id_espacio: int,
    datos: schemas.EspacioUpdate,
    db: Session = Depends(get_db)
):
    espacio = db.query(models.Espacio).filter(
        models.Espacio.id_espacio == id_espacio
    ).first()
    if not espacio:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(espacio, campo, valor)

    db.commit()
    db.refresh(espacio)
    return espacio


# ─────────────────────────────────────────
# ELIMINAR
# ─────────────────────────────────────────

@router.delete("/{id_espacio}", status_code=204)
def eliminar_espacio(id_espacio: int, db: Session = Depends(get_db)):
    espacio = db.query(models.Espacio).filter(
        models.Espacio.id_espacio == id_espacio
    ).first()
    if not espacio:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")

    db.delete(espacio)
    db.commit()


# ─────────────────────────────────────────
# CATÁLOGOS RELACIONADOS
# ─────────────────────────────────────────

@router.get("/catalogos/tipos", response_model=list[schemas.EspacioOut])
def listar_tipos_espacio(db: Session = Depends(get_db)):
    return db.query(models.TipoEspacio).all()


@router.get("/catalogos/edificios", response_model=list[schemas.EdificioOut])
def listar_edificios(db: Session = Depends(get_db)):
    return db.query(models.Edificio).all()


@router.get("/catalogos/pisos/{id_edificio}", response_model=list[schemas.PisoOut])
def listar_pisos(id_edificio: int, db: Session = Depends(get_db)):
    return db.query(models.Piso).filter(
        models.Piso.id_edificio == id_edificio
    ).all()