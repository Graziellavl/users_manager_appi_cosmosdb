from fastapi import FastAPI, HTTPException, Query, Path
from typing import List
from database import container_users, container_projects
from models import Usuario, Proyecto
from azure.cosmos import exceptions
from datetime import datetime

app = FastAPI(title="API de Gestión de Eventos y Participantes")

@app.get("/") #La raiz
def home():
    return "Hola Mundo"

@app.get("/usuarios/", response_model=List[Usuario])
def obtener_usuarios():
    query = "select * from c"
    items = list(container_users.query_items(query=query, enable_cross_partition_query=True))
    
    # print (len(items))
    if len(items) < 1:
        raise HTTPException(status_code=400, detail="No hay usuarios creados")
    else:
        return items

@app.post("/usuarios/", response_model=Usuario, status_code=201)
def crear_usuario(usuario: Usuario):
    query = "select * from c"
    users = list(container_users.query_items(query=query, enable_cross_partition_query=True))
    
    try:
        esigual = 0
        for e in users:
            if e['email'] == usuario.dict()['email']: #len(users) == 0: #
                esigual = 1

        if esigual == 1:
            raise HTTPException(status_code=400, detail="Ya existe un usuario registrado con ese correo.")
        elif usuario.dict()['edad'] < 18:
            raise HTTPException(status_code=400, detail="El usuario tiene que ser mayor de edad.")
        else:
            container_users.create_item(body=usuario.dict())
            return usuario

    except exceptions.CosmosResourceExistsError:
        raise HTTPException(status_code=400, detail="El usuario con este ID ya existe.")
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=tr(e))

@app.put("/usuario/{user_id}", response_model = Usuario)
def actualizar_usuario(user_id:str, actualizar_usuario:Usuario):
    usuario = container_users.read_item(item=user_id, partition_key = user_id)
    usuario.update(actualizar_usuario.dict(exclude_unset=True))

    query = "select * from c"
    users = list(container_users.query_items(query=query, enable_cross_partition_query=True))

    try:
        esigual = 0
        for e in users:
            if e['email'] == usuario['email'] and e['id'] != usuario['id']:
                esigual = 1

        if esigual == 1:
            raise HTTPException(status_code=400, detail="Ya existe un usuario con ese correo.")
        elif usuario['edad'] < 18:
            raise HTTPException(status_code=400, detail="El usuario tiene que ser mayor de edad.")
        else:
            container_users.replace_item(item=user_id, body=usuario)
            return usuario

    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail='Usuario no existe')
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/usuarios/{user_id}")
def eliminar_usuario(usuario_id: str):
    
    query = "select * from c"
    proyectos = list(container_projects.query_items(query=query, enable_cross_partition_query=True))

    try:
        usuario = container_users.read_item(item=usuario_id, partition_key=usuario_id)
        # usuario_con_proyecto = 0
        # for e in proyectos:
        #     if e['id_usuario'] == usuario.dict()['id']:
        #         usuario_con_proyecto = 1

        usuario_con_proyecto = next((p for p in proyectos if p['id_usuario'] == usuario_id), None)
        
        if usuario_con_proyecto:
            raise HTTPException(status_code=400, detail='El usuario está asignado a un proyecto')
        else:
            container_users.delete_item(item=usuario_id, partition_key=usuario_id)
            return usuario

        return
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/proyectos/", response_model=Proyecto, status_code=201)
def crear_proyecto(proyecto: Proyecto):
    query = "select * from c"
    users = list(container_projects.query_items(query=query, enable_cross_partition_query=True))
    
    try:
        container_projects.create_item(body=proyecto.dict())
        return proyecto

    except exceptions.CosmosResourceExistsError:
        raise HTTPException(status_code=400, detail="El proyecto con este ID ya existe.")
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=tr(e))



#Obtener participantes de un usuario
@app.get("/usuarios/{usuario_id}")
def obtener_proyectos_usuario(usuario_id: str):
    query = "select * from c"
    # usuarios = list(container_users.query_items(query=query, enable_cross_partition_query=True))
    
    # usuario = container_users.read_item(item=usuario_id, partition_key=usuario_id)
    
    try:
        usuario = container_users.read_item(item=usuario_id, partition_key=usuario_id)

        if not usuario:
            raise HTTPException(status_code=400, detail='El usuario no existe')
        else:
            proyectos = list(container_projects.query_items(query=query, enable_cross_partition_query=True))
            proyectos_usuario = next((p for p in proyectos if p['id_usuario'] == usuario_id), None)

            if not proyectos_usuario:
                raise HTTPException(status_code=400, detail='El usuario no tiene proyectos asignados')
            else:
                return proyectos_usuario 

    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail='El usuario no existe')
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.put("/proyecto/{proyecto_id}", response_model = Proyecto)
def actualizar_proyecto(proyecto_id:str, actualizar_proyecto:Proyecto):
    
    query = "select * from c"

    try:
        proyectonuevo = container_projects.read_item(item=proyecto_id, partition_key = proyecto_id)
        proyectonuevo.update(actualizar_proyecto.dict(exclude_unset=True))
        try:
            usuario = container_users.read_item(item=proyectonuevo['id_usuario'], partition_key=proyectonuevo['id_usuario'])
        except exceptions.CosmosResourceNotFoundError:
            raise HTTPException(status_code=404, detail='El usuario no existe')
        
        if proyectonuevo['id'] != proyecto_id:
            raise HTTPException(status_code=400, detail="No se puede actualizar el ID del proyecto.")
            try:
                proyectos = list(container_projects.query_items(query=query, enable_cross_partition_query=True))
                proyectos_usuario = next((p for p in proyectos if p['id_usuario'] == proyectonuevo['id_usuario']), None)
            except:
                if not proyectos_usuario:
                    container_projects.replace_item(item=proyecto_id, body=proyectonuevo)
                    return proyectonuevo
                
            if len(proyectos_usuario) > 2:
                raise HTTPException(status_code=400, detail="El usuario no puede estar asignado a más de 2 proyectos.")

    except exceptions.CosmosResourceNotFoundError:
            raise HTTPException(status_code=404, detail='El proyecto no existe')
    except exceptions.CosmosHttpResponseError as e:
            raise HTTPException(status_code=400, detail=str(e))



@app.delete("/proyectos/{proyecto_id}")
def eliminar_proyecto(proyecto_id: str):
    
    try:        
        container_projects.delete_item(item=proyecto_id, partition_key=proyecto_id)
        return
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))