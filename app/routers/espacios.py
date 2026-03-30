from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app import models, schemas

router = APIRouter(tags=["Espacios"])

# ─────────────────────────────────────────
# CATÁLOGOS (PRIMERO)
# ─────────────────────────────────────────

@router.get("/catalogos/tipos", response_model=list[schemas.TipoEspacioOut])
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


@router.get("/catalogos/equipamiento", response_model=list[schemas.TipoEquipamientoOut])
def listar_tipos_equipamiento(db: Session = Depends(get_db)):
    return db.query(models.TipoEquipamiento).all()


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
        raise HTTPException(
            status_code=400,
            detail="Ya existe un espacio con ese código"
        )

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

@router.get("/admin/fix-secuencia-espacios")
def fix_secuencia_espacios(db: Session = Depends(get_db)):
    try:
        db.execute(text("""
            SELECT setval(
                pg_get_serial_sequence('espacio', 'id_espacio'),
                (SELECT MAX(id_espacio) FROM espacio)
            )
        """))
        db.commit()
        return {"ok": True, "mensaje": "Secuencia de espacios corregida"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

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
# EQUIPAMIENTO DE ESPACIOS
# ─────────────────────────────────────────

@router.get("/admin/fix-secuencia")
def fix_secuencia(db: Session = Depends(get_db)):
    try:
        db.execute(text("""
            SELECT setval(
                pg_get_serial_sequence('espacioequipamiento', 'id_espacio_equipamiento'),
                (SELECT MAX(id_espacio_equipamiento) FROM espacioequipamiento)
            )
        """))
        db.commit()
        return {"ok": True, "mensaje": "Secuencia corregida"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.get("/{id_espacio}/equipamiento", response_model=list[schemas.EspacioEquipamientoOut])
def listar_equipamiento_espacio(id_espacio: int, db: Session = Depends(get_db)):

    rows = db.query(models.EspacioEquipamiento).filter(
        models.EspacioEquipamiento.id_espacio == id_espacio
    ).all()

    result = []

    for row in rows:
        result.append({
            "id_espacio_equipamiento": row.id_espacio_equipamiento,
            "id_tipo_equipamiento": row.id_tipo_equipamiento,
            "nombre_tipo_equipamiento": row.tipo_equipamiento.nombre_tipo_equipamiento
        })

    return result

@router.post("/{id_espacio}/equipamiento", status_code=201)
def agregar_equipamiento(
    id_espacio: int,
    datos: schemas.EquipamientoAsignarRequest,
    db: Session = Depends(get_db)
):

    existe = db.query(models.EspacioEquipamiento).filter(
        models.EspacioEquipamiento.id_espacio == id_espacio,
        models.EspacioEquipamiento.id_tipo_equipamiento == datos.id_tipo_equipamiento
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Este equipamiento ya está asignado al espacio"
        )

    nuevo = models.EspacioEquipamiento(
        id_espacio=id_espacio,
        id_tipo_equipamiento=datos.id_tipo_equipamiento
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return {
        "id_espacio_equipamiento": nuevo.id_espacio_equipamiento,
        "id_tipo_equipamiento": nuevo.id_tipo_equipamiento,
        "nombre_tipo_equipamiento": nuevo.tipo_equipamiento.nombre_tipo_equipamiento
    }


@router.delete("/{id_espacio}/equipamiento/{id_equip}", status_code=204)
def eliminar_equipamiento(id_espacio: int, id_equip: int, db: Session = Depends(get_db)):

    row = db.query(models.EspacioEquipamiento).filter(
        models.EspacioEquipamiento.id_espacio_equipamiento == id_equip,
        models.EspacioEquipamiento.id_espacio == id_espacio
    ).first()

    if not row:
        raise HTTPException(status_code=404, detail="Equipamiento no encontrado")

    db.delete(row)
    db.commit()