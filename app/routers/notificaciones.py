from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(tags=["Notificaciones"])

# ─────────────────────────────────────────
# LISTAR POR USUARIO
# ─────────────────────────────────────────

@router.get("/usuario/{id_usuario}", response_model=list[schemas.NotificacionOut])
def notificaciones_por_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return db.query(models.Notificacion).filter(
        models.Notificacion.id_usuario_destino == id_usuario
    ).order_by(models.Notificacion.fecha_envio.desc()).all()


# ─────────────────────────────────────────
# LISTAR NO LEÍDAS
# ─────────────────────────────────────────

@router.get("/usuario/{id_usuario}/no-leidas", response_model=list[schemas.NotificacionOut])
def notificaciones_no_leidas(id_usuario: int, db: Session = Depends(get_db)):
    return db.query(models.Notificacion).filter(
        models.Notificacion.id_usuario_destino == id_usuario,
        models.Notificacion.leida == 0
    ).order_by(models.Notificacion.fecha_envio.desc()).all()


# ─────────────────────────────────────────
# CONTAR NO LEÍDAS
# ─────────────────────────────────────────

@router.get("/usuario/{id_usuario}/contador")
def contar_no_leidas(id_usuario: int, db: Session = Depends(get_db)):
    total = db.query(models.Notificacion).filter(
        models.Notificacion.id_usuario_destino == id_usuario,
        models.Notificacion.leida == 0
    ).count()
    return {"id_usuario": id_usuario, "no_leidas": total}


# ─────────────────────────────────────────
# MARCAR UNA COMO LEÍDA
# ─────────────────────────────────────────

@router.put("/{id_notificacion}/leer", response_model=schemas.NotificacionOut)
def marcar_leida(id_notificacion: int, db: Session = Depends(get_db)):
    notif = db.query(models.Notificacion).filter(
        models.Notificacion.id_notificacion == id_notificacion
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    notif.leida = 1
    db.commit()
    db.refresh(notif)
    return notif


# ─────────────────────────────────────────
# MARCAR TODAS COMO LEÍDAS
# ─────────────────────────────────────────

@router.put("/usuario/{id_usuario}/leer-todas")
def marcar_todas_leidas(id_usuario: int, db: Session = Depends(get_db)):
    db.query(models.Notificacion).filter(
        models.Notificacion.id_usuario_destino == id_usuario,
        models.Notificacion.leida == 0
    ).update({"leida": 1})
    db.commit()
    return {"mensaje": "Todas las notificaciones marcadas como leídas"}


# ─────────────────────────────────────────
# ELIMINAR UNA
# ─────────────────────────────────────────

@router.delete("/{id_notificacion}", status_code=204)
def eliminar_notificacion(id_notificacion: int, db: Session = Depends(get_db)):
    notif = db.query(models.Notificacion).filter(
        models.Notificacion.id_notificacion == id_notificacion
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    db.delete(notif)
    db.commit()