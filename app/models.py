from sqlalchemy import Column, Integer, String, Text, Date, Time, DateTime, SmallInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Rol(Base):
    __tablename__ = "rol"
    id_rol     = Column(Integer, primary_key=True, index=True)
    nombre_rol = Column(String(100), nullable=False)
    usuarios   = relationship("Usuario", back_populates="rol")

class Carrera(Base):
    __tablename__ = "carrera"
    id_carrera     = Column(Integer, primary_key=True, index=True)
    nombre_carrera = Column(String(200), nullable=False)
    clave_carrera  = Column(String(20))
    usuarios       = relationship("Usuario", back_populates="carrera")

class Usuario(Base):
    __tablename__ = "usuario"
    id_usuario   = Column(Integer, primary_key=True, index=True)
    matricula    = Column(String(20),  unique=True)
    nombre       = Column(String(100), nullable=False)
    apellido_p   = Column(String(100), nullable=False)
    apellido_m   = Column(String(100))
    correo       = Column(String(200), unique=True, nullable=False)
    contrasenia  = Column(String(255), nullable=False)
    cuatrimestre = Column(Integer)
    id_rol       = Column(Integer, ForeignKey("rol.id_rol"),         nullable=False)
    id_carrera   = Column(Integer, ForeignKey("carrera.id_carrera"))
    rol                = relationship("Rol",     back_populates="usuarios")
    carrera            = relationship("Carrera", back_populates="usuarios")
    reservaciones      = relationship("Reservacion",    back_populates="usuario")
    notificaciones     = relationship("Notificacion",   back_populates="usuario_destino")
    gestiones          = relationship("Gestion",        back_populates="gestor")
    espacios_asignados = relationship("EncargadoEspacio", back_populates="usuario")

class Edificio(Base):
    __tablename__ = "edificio"
    id_edificio     = Column(Integer, primary_key=True, index=True)
    nombre_edificio = Column(String(100), nullable=False)
    clave_edificio  = Column(String(20))
    pisos           = relationship("Piso", back_populates="edificio")

class Piso(Base):
    __tablename__ = "piso"
    id_piso     = Column(Integer, primary_key=True, index=True)
    numero_piso = Column(String(50), nullable=False)
    id_edificio = Column(Integer, ForeignKey("edificio.id_edificio"), nullable=False)
    edificio  = relationship("Edificio", back_populates="pisos")
    espacios  = relationship("Espacio",  back_populates="piso")

class TipoEspacio(Base):
    __tablename__ = "tipoespacio"
    id_tipo_espacio     = Column(Integer, primary_key=True, index=True)
    nombre_tipo_espacio = Column(String(100), nullable=False)
    espacios            = relationship("Espacio", back_populates="tipo_espacio")

class EstadoEspacio(Base):
    __tablename__ = "estadoespacio"
    id_estado_espacio     = Column(Integer, primary_key=True, index=True)
    nombre_estado_espacio = Column(String(50), nullable=False)
    espacios              = relationship("Espacio", back_populates="estado_espacio")

class EstadoReservacion(Base):
    __tablename__ = "estadoreservacion"
    id_estado_reservacion     = Column(Integer, primary_key=True, index=True)
    nombre_estado_reservacion = Column(String(50), nullable=False)
    reservaciones = relationship("Reservacion", back_populates="estado_reservacion")
    gestiones     = relationship("Gestion",     back_populates="estado_reservacion")

class TipoEquipamiento(Base):
    __tablename__ = "tipoequipamiento"
    id_tipo_equipamiento     = Column(Integer, primary_key=True, index=True)
    nombre_tipo_equipamiento = Column(String(100), nullable=False)
    equipamientos            = relationship("EspacioEquipamiento", back_populates="tipo_equipamiento")

class Espacio(Base):
    __tablename__ = "espacio"
    id_espacio          = Column(Integer, primary_key=True, index=True)
    codigo_espacio      = Column(String(20),  nullable=False)
    nombre_espacio      = Column(String(150), nullable=False)
    descripcion_espacio = Column(Text)
    capacidad           = Column(Integer)
    id_tipo_espacio     = Column(Integer, ForeignKey("tipoespacio.id_tipo_espacio"),   nullable=False)
    id_estado_espacio   = Column(Integer, ForeignKey("estadoespacio.id_estado_espacio"), nullable=False)
    id_piso             = Column(Integer, ForeignKey("piso.id_piso"),                 nullable=False)
    tipo_espacio   = relationship("TipoEspacio",   back_populates="espacios")
    estado_espacio = relationship("EstadoEspacio", back_populates="espacios")
    piso           = relationship("Piso",          back_populates="espacios")
    equipamientos  = relationship("EspacioEquipamiento", back_populates="espacio")
    horarios       = relationship("HorarioEspacio",      back_populates="espacio")
    servicios      = relationship("Servicio",            back_populates="espacio")
    reservaciones  = relationship("Reservacion",         back_populates="espacio")
    encargados     = relationship("EncargadoEspacio",    back_populates="espacio")

class EspacioEquipamiento(Base):
    __tablename__ = "espacioequipamiento"
    id_espacio_equipamiento = Column(Integer, primary_key=True, index=True)
    id_espacio              = Column(Integer, ForeignKey("espacio.id_espacio"),                       nullable=False)
    id_tipo_equipamiento    = Column(Integer, ForeignKey("tipoequipamiento.id_tipo_equipamiento"),    nullable=False)
    espacio           = relationship("Espacio",           back_populates="equipamientos")
    tipo_equipamiento = relationship("TipoEquipamiento",  back_populates="equipamientos")

class HorarioEspacio(Base):
    __tablename__ = "horarioespacio"
    id_horario  = Column(Integer, primary_key=True, index=True)
    hora_inicio = Column(Time, nullable=False)
    hora_fin    = Column(Time, nullable=False)
    id_espacio  = Column(Integer, ForeignKey("espacio.id_espacio"), nullable=False)
    activo      = Column(SmallInteger, default=1)
    espacio     = relationship("Espacio", back_populates="horarios")

class TipoServicio(Base):
    __tablename__ = "tiposervicio"
    id_tipo_servicio     = Column(Integer, primary_key=True, index=True)
    nombre_tipo_servicio = Column(String(100), nullable=False)
    servicios            = relationship("Servicio", back_populates="tipo_servicio")

class Servicio(Base):
    __tablename__ = "servicio"
    id_servicio      = Column(Integer, primary_key=True, index=True)
    nombre_servicio  = Column(String(150), nullable=False)
    descripcion      = Column(Text)
    id_tipo_servicio = Column(Integer, ForeignKey("tiposervicio.id_tipo_servicio"), nullable=False)
    id_espacio       = Column(Integer, ForeignKey("espacio.id_espacio"),            nullable=False)
    disponible       = Column(SmallInteger, default=1)
    tipo_servicio        = relationship("TipoServicio",       back_populates="servicios")
    espacio              = relationship("Espacio",             back_populates="servicios")
    reservacion_servicios = relationship("ReservacionServicio", back_populates="servicio")

class EncargadoEspacio(Base):
    __tablename__ = "encargadoespacio"
    id_encargado_espacio = Column(Integer, primary_key=True, index=True)
    id_usuario           = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    id_espacio           = Column(Integer, ForeignKey("espacio.id_espacio"), nullable=False)
    fecha_asignacion     = Column(Date)
    usuario = relationship("Usuario", back_populates="espacios_asignados")
    espacio = relationship("Espacio",  back_populates="encargados")

class Reservacion(Base):
    __tablename__ = "reservacion"
    id_reservacion        = Column(Integer, primary_key=True, index=True)
    folio_reservacion     = Column(String(50), unique=True, nullable=False)
    fecha_solicitud       = Column(DateTime, server_default=func.now())
    fecha_reserva         = Column(Date, nullable=False)
    hora_inicio           = Column(Time, nullable=False)
    hora_fin              = Column(Time, nullable=False)
    capacidad_solicitada  = Column(Integer)
    motivo                = Column(Text)
    id_usuario            = Column(Integer, ForeignKey("usuario.id_usuario"),                       nullable=False)
    id_espacio            = Column(Integer, ForeignKey("espacio.id_espacio"),                       nullable=False)
    id_estado_reservacion = Column(Integer, ForeignKey("estadoreservacion.id_estado_reservacion"),  nullable=False)
    usuario            = relationship("Usuario",          back_populates="reservaciones")
    espacio            = relationship("Espacio",          back_populates="reservaciones")
    estado_reservacion = relationship("EstadoReservacion", back_populates="reservaciones")
    gestiones          = relationship("Gestion",          back_populates="reservacion")
    notificaciones     = relationship("Notificacion",     back_populates="reservacion")
    servicios          = relationship("ReservacionServicio", back_populates="reservacion")

class ReservacionServicio(Base):
    __tablename__ = "reservacionservicio"
    id_reservacion_servicio = Column(Integer, primary_key=True, index=True)
    id_reservacion          = Column(Integer, ForeignKey("reservacion.id_reservacion"), nullable=False)
    id_servicio             = Column(Integer, ForeignKey("servicio.id_servicio"),       nullable=False)
    reservacion = relationship("Reservacion", back_populates="servicios")
    servicio    = relationship("Servicio",    back_populates="reservacion_servicios")

class Gestion(Base):
    __tablename__ = "gestion"
    id_gestion            = Column(Integer, primary_key=True, index=True)
    id_reservacion        = Column(Integer, ForeignKey("reservacion.id_reservacion"),               nullable=False)
    id_usuario_gestor     = Column(Integer, ForeignKey("usuario.id_usuario"),                       nullable=False)
    fecha_gestion         = Column(DateTime, server_default=func.now())
    id_estado_reservacion = Column(Integer, ForeignKey("estadoreservacion.id_estado_reservacion"),  nullable=False)
    observaciones         = Column(Text)
    reservacion        = relationship("Reservacion",      back_populates="gestiones")
    gestor             = relationship("Usuario",          back_populates="gestiones")
    estado_reservacion = relationship("EstadoReservacion", back_populates="gestiones")

class TipoNotificacion(Base):
    __tablename__ = "tiponotificacion"
    id_tipo_notificacion     = Column(Integer, primary_key=True, index=True)
    nombre_tipo_notificacion = Column(String(100), nullable=False)
    notificaciones           = relationship("Notificacion", back_populates="tipo_notificacion")

class Notificacion(Base):
    __tablename__ = "notificacion"
    id_notificacion      = Column(Integer, primary_key=True, index=True)
    id_usuario_destino   = Column(Integer, ForeignKey("usuario.id_usuario"),                         nullable=False)
    id_reservacion       = Column(Integer, ForeignKey("reservacion.id_reservacion"))
    id_tipo_notificacion = Column(Integer, ForeignKey("tiponotificacion.id_tipo_notificacion"),       nullable=False)
    titulo_notificacion  = Column(String(255), nullable=False)
    cuerpo_notificacion  = Column(Text)
    leida                = Column(SmallInteger, default=0)
    fecha_envio          = Column(DateTime, server_default=func.now())
    usuario_destino  = relationship("Usuario",          back_populates="notificaciones")
    reservacion      = relationship("Reservacion",      back_populates="notificaciones")
    tipo_notificacion = relationship("TipoNotificacion", back_populates="notificaciones")