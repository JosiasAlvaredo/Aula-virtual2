drop database if exists aula_virtual;
create database aula_virtual;
use aula_virtual;

create table usuarios (
	id_usuario int auto_increment primary key,
    nombre varchar(30),
    apellido varchar(30),
    posicion enum('A','P','E') not null default 'E' comment 'A = admin, P = profesor, E = estudiante',
    email varchar(50) unique,
    contrasena varchar(20),
    foto_perfil varchar(255),
    fecha_registro datetime default current_timestamp
);

create table clases (
	id_clase int auto_increment primary key,
    nombre_clase varchar(30),
    codigo_ingreso varchar(10) unique,
    banner varchar(255),
    descripcion text,
    fecha_creacion datetime default current_timestamp
);

create table ingresos (
	id_ingreso int auto_increment primary key,
	id_clase int,
    id_usuario int,
    fecha_ingreso datetime default current_timestamp,
    foreign key (id_clase) references clases (id_clase),
    foreign key (id_usuario) references usuarios (id_usuario)
);

create table publicaciones (
	id_publicacion int auto_increment primary key,
    id_clase int,
    id_creador int,
    fecha_publicacion datetime default current_timestamp,
    entregable bool,
    fecha_entrega datetime,
    bloquear_entrega bool,
    mensaje varchar(500),
    multimedia varchar(255),
    foreign key (id_clase) references clases (id_clase),
	foreign key (id_creador) references usuarios (id_usuario)
);

create table foros (
	id_foro int auto_increment primary key,
    id_clase int,
    id_creador int,
    fecha_creacion datetime default current_timestamp,
    titulo varchar(100),
    descripcion text,
    foreign key (id_clase) references clases (id_clase),
	foreign key (id_creador) references usuarios (id_usuario)
);

create table entregas (
	id_entrega int auto_increment primary key,
    id_tarea int,
    id_alumno int,
    fecha_entrega datetime default current_timestamp,
    multimedia varchar(255),
    foreign key (id_tarea) references publicaciones (id_publicacion),
    foreign key (id_alumno) references usuarios (id_usuario)
);

create table devoluciones (
	id_devolucion int auto_increment primary key,
    id_entrega int,
    id_profesor int,
    calificacion int,
    aclaraciones varchar(250),
    fecha_devolucion datetime default current_timestamp,
    foreign key (id_entrega) references entregas (id_entrega),
    foreign key (id_profesor) references usuarios (id_usuario)
);

create table mensajes_privados (
	id_mensaje int auto_increment primary key,
    id_publicacion int,
    id_emisor int,
    id_receptor int,
    mensaje varchar(250),
    multimedia varchar(255),
    fecha_envio datetime default current_timestamp,
    foreign key (id_publicacion) references publicaciones (id_publicacion),
    foreign key (id_emisor) references usuarios (id_usuario),
    foreign key (id_receptor) references usuarios (id_usuario)
);

create table mensajes_foro (
	id_mensaje int auto_increment primary key,
    id_foro int,
    id_emisor int,
    mensaje varchar(250),
    multimedia varchar(255),
    fecha_envio datetime default current_timestamp,
    foreign key (id_foro) references foros (id_foro),
    foreign key (id_emisor) references usuarios (id_usuario)
);
