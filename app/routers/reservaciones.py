from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app import models, schemas
import random
import string

router = APIRouter(tags=["Reservaciones"])

# ─────────────────────────────────────────
# UTILIDAD — GENERAR FOLIO
# ─────────────────────────────────────────

def generar_folio() -> str:
    año = datetime.now().year
    aleatorio = ''.join(random.choices(string.digits, k=4))
    return f"RES-{año}-{aleatorio}"


# ─────────────────────────────────────────
# LISTAR TODAS
# ─────────────────────────────────────────

@router.get("/", response_model=list[schemas.ReservacionOut])
def listar_reservaciones(db: Session = Depends(get_db)):
    return db.query(models.Reservacion).all()


# ─────────────────────────────────────────
# LISTAR POR USUARIO
# ─────────────────────────────────────────

@router.get("/usuario/{id_usuario}", response_model=list[schemas.ReservacionOut])
def reservaciones_por_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return db.query(models.Reservacion).filter(
        models.Reservacion.id_usuario == id_usuario
    ).all()


# ─────────────────────────────────────────
# LISTAR POR ESTADO
# ─────────────────────────────────────────

@router.get("/estado/{id_estado}", response_model=list[schemas.ReservacionOut])
def reservaciones_por_estado(id_estado: int, db: Session = Depends(get_db)):
    return db.query(models.Reservacion).filter(
        models.Reservacion.id_estado_reservacion == id_estado
    ).all()


# ─────────────────────────────────────────
# GESTIONAR (aprobar / rechazar — encargado)
# ─────────────────────────────────────────

@router.post("/gestionar", response_model=schemas.GestionOut, status_code=201)
def gestionar_reservacion(
    datos: schemas.GestionCreate,
    db: Session = Depends(get_db)
):
    reservacion = db.query(models.Reservacion).filter(
        models.Reservacion.id_reservacion == datos.id_reservacion
    ).first()
    if not reservacion:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")

    # Registrar la gestión
    gestion = models.Gestion(
        id_reservacion        = datos.id_reservacion,
        id_usuario_gestor     = datos.id_usuario_gestor,
        id_estado_reservacion = datos.id_estado_reservacion,
        observaciones         = datos.observaciones,
    )
    db.add(gestion)

    # Actualizar estado de la reservación
    reservacion.id_estado_reservacion = datos.id_estado_reservacion

    # Si fue rechazada o cancelada liberar el espacio
    if datos.id_estado_reservacion in [3, 4]:
        espacio = db.query(models.Espacio).filter(
            models.Espacio.id_espacio == reservacion.id_espacio
        ).first()
        if espacio:
            espacio.id_estado_espacio = 1  # Disponible

    db.commit()
    db.refresh(gestion)

    # Notificación al usuario solicitante
    tipo_notif = 1 if datos.id_estado_reservacion == 2 else 2  # Aprobacion o Rechazo
    titulo     = "Reservación aprobada" if datos.id_estado_reservacion == 2 else "Reservación rechazada"
    cuerpo     = datos.observaciones or titulo

    notif = models.Notificacion(
        id_usuario_destino   = reservacion.id_usuario,
        id_reservacion       = datos.id_reservacion,
        id_tipo_notificacion = tipo_notif,
        titulo_notificacion  = titulo,
        cuerpo_notificacion  = cuerpo,
        leida                = 0,
    )
    db.add(notif)
    db.commit()

    return gestion

# ─────────────────────────────────────────
# OBTENER UNA
# ─────────────────────────────────────────

@router.get("/{id_reservacion}", response_model=schemas.ReservacionOut)
def obtener_reservacion(id_reservacion: int, db: Session = Depends(get_db)):
    reservacion = db.query(models.Reservacion).filter(
        models.Reservacion.id_reservacion == id_reservacion
    ).first()
    if not reservacion:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    return reservacion


# ─────────────────────────────────────────
# CREAR
# ─────────────────────────────────────────

@router.post("/{id_usuario}", response_model=schemas.ReservacionOut, status_code=201)
def crear_reservacion(
    id_usuario: int,
    datos: schemas.ReservacionCreate,
    db: Session = Depends(get_db)
):
    # Verificar que el usuario existe
    usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == id_usuario
    ).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar que el espacio existe y está disponible
    espacio = db.query(models.Espacio).filter(
        models.Espacio.id_espacio == datos.id_espacio
    ).first()
    if not espacio:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    if espacio.id_estado_espacio != 1:
        raise HTTPException(status_code=400, detail="El espacio no está disponible")

    # Verificar que no haya choque de horario ese día
    choque = db.query(models.Reservacion).filter(
        models.Reservacion.id_espacio        == datos.id_espacio,
        models.Reservacion.fecha_reserva     == datos.fecha_reserva,
        models.Reservacion.id_estado_reservacion.in_([1, 2]),
        models.Reservacion.hora_inicio       < datos.hora_fin,
        models.Reservacion.hora_fin          > datos.hora_inicio,
    ).first()
    if choque:
        raise HTTPException(status_code=400, detail="El espacio ya tiene una reservación en ese horario")

    # Generar folio único
    folio = generar_folio()
    while db.query(models.Reservacion).filter(
        models.Reservacion.folio_reservacion == folio
    ).first():
        folio = generar_folio()

    nueva = models.Reservacion(
        folio_reservacion     = folio,
        fecha_reserva         = datos.fecha_reserva,
        hora_inicio           = datos.hora_inicio,
        hora_fin              = datos.hora_fin,
        capacidad_solicitada  = datos.capacidad_solicitada,
        motivo                = datos.motivo,
        id_usuario            = id_usuario,
        id_espacio            = datos.id_espacio,
        id_estado_reservacion = 1,  # Pendiente
    )
    db.add(nueva)

    # Cambiar estado del espacio a "Reservado Temporalmente"
    espacio.id_estado_espacio = 2
    db.commit()
    db.refresh(nueva)

    # Crear notificación automática para el usuario
    notif = models.Notificacion(
        id_usuario_destino   = id_usuario,
        id_reservacion       = nueva.id_reservacion,
        id_tipo_notificacion = 4,  # Sistema
        titulo_notificacion  = "Solicitud enviada",
        cuerpo_notificacion  = f"Tu solicitud {folio} fue recibida y está pendiente de aprobación.",
        leida                = 0,
    )
    db.add(notif)
    db.commit()

    return nueva


# ─────────────────────────────────────────
# CANCELAR (por el usuario)
# ─────────────────────────────────────────

@router.put("/{id_reservacion}/cancelar", response_model=schemas.ReservacionOut)
def cancelar_reservacion(id_reservacion: int, db: Session = Depends(get_db)):
    reservacion = db.query(models.Reservacion).filter(
        models.Reservacion.id_reservacion == id_reservacion
    ).first()
    if not reservacion:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    if reservacion.id_estado_reservacion not in [1, 2]:
        raise HTTPException(status_code=400, detail="Solo se pueden cancelar reservaciones pendientes o aprobadas")

    reservacion.id_estado_reservacion = 4  # Cancelada

    # Liberar el espacio
    espacio = db.query(models.Espacio).filter(
        models.Espacio.id_espacio == reservacion.id_espacio
    ).first()
    if espacio:
        espacio.id_estado_espacio = 1  # Disponible

    db.commit()
    db.refresh(reservacion)

    # Notificación de cancelación
    notif = models.Notificacion(
        id_usuario_destino   = reservacion.id_usuario,
        id_reservacion       = id_reservacion,
        id_tipo_notificacion = 3,  # Cancelacion
        titulo_notificacion  = "Reservación cancelada",
        cuerpo_notificacion  = f"Tu reservación {reservacion.folio_reservacion} fue cancelada.",
        leida                = 0,
    )
    db.add(notif)
    db.commit()

    return reservacion

