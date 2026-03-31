from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, time, datetime

# ─────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────

class LoginRequest(BaseModel):
    correo: str
    contrasenia: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id_usuario: Optional[int] = None

# ─────────────────────────────────────────
# ROL
# ─────────────────────────────────────────

class RolBase(BaseModel):
    nombre_rol: str

class RolOut(RolBase):
    id_rol: int
    class Config:
        from_attributes = True

# ─────────────────────────────────────────
# CARRERA
# ─────────────────────────────────────────

class CarreraBase(BaseModel):
    nombre_carrera: str
    clave_carrera:  Optional[str] = None

class CarreraOut(CarreraBase):
    id_carrera: int
    class Config:
        from_attributes = True

# ─────────────────────────────────────────
# USUARIO
# ─────────────────────────────────────────

class UsuarioCreate(BaseModel):
    matricula:    Optional[str] = None
    nombre:       str
    apellido_p:   str
    apellido_m:   Optional[str] = None
    correo:       str
    contrasenia:  str
    cuatrimestre: Optional[int] = None
    id_rol:       int
    id_carrera:   Optional[int] = None

class UsuarioUpdate(BaseModel):
    nombre:       Optional[str] = None
    apellido_p:   Optional[str] = None
    apellido_m:   Optional[str] = None
    cuatrimestre: Optional[int] = None
    id_carrera:   Optional[int] = None

class UsuarioOut(BaseModel):
    id_usuario:   int
    matricula:    Optional[str]
    nombre:       str
    apellido_p:   str
    apellido_m:   Optional[str]
    correo:       str
    cuatrimestre: Optional[int]
    id_rol:       int
    id_carrera:   Optional[int]
    class Config:
        from_attributes = True

# ─────────────────────────────────────────
# EDIFICIO Y PISO
# ─────────────────────────────────────────

class EdificioOut(BaseModel):
    id_edificio:     int
    nombre_edificio: str
    clave_edificio:  Optional[str]
    class Config:
        from_attributes = True

class PisoOut(BaseModel):
    id_piso:     int
    numero_piso: str
    id_edificio: int
    class Config:
        from_attributes = True

# ─────────────────────────────────────────
# ESPACIO
# ─────────────────────────────────────────

class EspacioCreate(BaseModel):
    codigo_espacio:      str
    nombre_espacio:      str
    descripcion_espacio: Optional[str] = None
    capacidad:           Optional[int] = None
    id_tipo_espacio:     int
    id_estado_espacio:   int
    id_piso:             int

class EspacioUpdate(BaseModel):
    nombre_espacio:      Optional[str] = None
    descripcion_espacio: Optional[str] = None
    capacidad:           Optional[int] = None
    id_estado_espacio:   Optional[int] = None

class EspacioOut(BaseModel):
    id_espacio:          int
    codigo_espacio:      str
    nombre_espacio:      str
    descripcion_espacio: Optional[str]
    capacidad:           Optional[int]
    id_tipo_espacio:     int
    id_estado_espacio:   int
    id_piso:             int
    class Config:
        from_attributes = True

# ─────────────────────────────────────────
# RESERVACION
# ─────────────────────────────────────────

class ReservacionCreate(BaseModel):
    fecha_reserva:        date
    hora_inicio:          time
    hora_fin:             time
    capacidad_solicitada: Optional[int] = None
    motivo:               Optional[str] = None
    id_espacio:           int

class ReservacionOut(BaseModel):
    id_reservacion:        int
    folio_reservacion:     str
    fecha_solicitud:       Optional[datetime]
    fecha_reserva:         date
    hora_inicio:           time
    hora_fin:              time
    capacidad_solicitada:  Optional[int]
    motivo:                Optional[str]
    id_usuario:            int
    id_espacio:            int
    id_estado_reservacion: int
    class Config:
        from_attributes = True

# ─────────────────────────────────────────
# GESTIÓN
# ─────────────────────────────────────────

class GestionCreate(BaseModel):
    id_reservacion:        int
    id_usuario_gestor:     int
    id_estado_reservacion: int
    observaciones:         Optional[str] = None

class GestionOut(BaseModel):
    id_gestion:            int
    id_reservacion:        int
    id_usuario_gestor:     int
    fecha_gestion:         Optional[datetime]
    id_estado_reservacion: int
    observaciones:         Optional[str]
    class Config:
        from_attributes = True

# ─────────────────────────────────────────
# NOTIFICACION
# ─────────────────────────────────────────

class NotificacionOut(BaseModel):
    id_notificacion:      int
    id_usuario_destino:   int
    id_reservacion:       Optional[int]
    id_tipo_notificacion: int
    titulo_notificacion:  str
    cuerpo_notificacion:  Optional[str]
    leida:                int
    fecha_envio:          Optional[datetime]
    class Config:
        from_attributes = True

class MarcarLeidaRequest(BaseModel):
    id_notificacion: int

class TipoEspacioOut(BaseModel):
    id_tipo_espacio:     int
    nombre_tipo_espacio: str
    class Config:
        from_attributes = True

class TipoEquipamientoOut(BaseModel):
    id_tipo_equipamiento:     int
    nombre_tipo_equipamiento: str
    class Config:
        from_attributes = True
 
class EspacioEquipamientoOut(BaseModel):
    id_espacio_equipamiento:  int
    id_tipo_equipamiento:     int
    nombre_tipo_equipamiento: str
    class Config:
        from_attributes = True
 
class EquipamientoAsignarRequest(BaseModel):
    id_tipo_equipamiento: int
 