from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
from typing import List
from models import TaskCreate, Task
from storage import read_tasks, write_tasks



app = FastAPI(title="ToDo API")

@app.get("/")
def root():
    """
    Ruta raíz para verificar si la API está funcionando correctamente. 
    Si la API está en funcionamiento, devuelve un mensaje de estado.

    Returns:
        dict: Mensaje de estado de la API.
    """
    
    return {"ok": True, "message": "API funcionando!"}



@app.get("/tasks", response_model=List[Task])
def get_tasks():
    """
    Ruta para obtener todas las tareas.

    Returns:
    list: Lista de tareas.
    """
    
    return read_tasks()


@app.post("/tasks", response_model=Task)
def create_task(task_in: TaskCreate):
    """
    Ruta para crear una nueva tarea.Si el archivo de tareas no existe, se crea uno nuevo con la tarea. Si el archivo ya existe, se agrega la nueva tarea a la lista existente.

    Args:
    task_in (TaskCreate): Datos de la tarea a crear.

    Returns:
    dict: La tarea creada.
    """
    
    tasks = read_tasks()
    if not tasks:
        next_id = 1   
    else:
        
        next_id = max(t["id"] for t in tasks) + 1    
    new_task = {
        "id": next_id,
        "title": task_in.title, 
        "description": task_in.description, 
        "status": "pendiente",
        "priority": task_in.priority,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    tasks.append(new_task)
    write_tasks(tasks) 
    return new_task



@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    """
    Ruta para obtener una tarea específica por su ID. Busca la tarea en la lista de tareas y la devuelve si se encuentra. Si no se encuentra, lanza una excepción HTTP 404.

    Args:
        task_id (int): ID de la tarea a obtener.
        

    Raises:
        HTTPException: Si la tarea no se encuentra, se lanza una excepción HTTP 404 con un mensaje de error.

    Returns:
        dict: La tarea encontrada.
        
    """
    tasks = read_tasks()

    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(status_code=404, detail="Tarea no encontrada")



@app.put("/tasks/{task_id}", response_model=Task)
def complete_task(task_id: int):
    """
    Ruta para marcar una tarea como completada por su ID. Busca la tarea en la lista de tareas y cambia su estado a "completada" si se encuentra. Si no se encuentra, lanza una excepción HTTP 404.

    Args:
        task_id (int): ID de la tarea a marcar como completada. 

    Raises:
        HTTPException: Si la tarea no se encuentra, se lanza una excepción HTTP 404 con un mensaje de error.

    Returns:
        dict: La tarea actualizada con el estado "completada".  
        
    """
    tasks = read_tasks()

    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "completada"
            write_tasks(tasks)
            return task
        
    raise HTTPException(status_code=404, detail="Tarea no encontrada")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    """
    Ruta para eliminar una tarea por su ID. Busca la tarea en la lista de tareas y la elimina si se encuentra. Si no se encuentra, lanza una excepción HTTP 404.

Args:
    task_id (int): ID de la tarea a eliminar.

    Raises:
    HTTPException: Si la tarea no se encuentra, se lanza una excepción HTTP 404 con un mensaje de error.
    
    Returns:
    dict: Mensaje de confirmación de que la tarea ha sido eliminada correctamente.
    """
    tasks = read_tasks()

    new_tasks = [task for task in tasks if task["id"] != task_id]

    if len(new_tasks) == len(tasks):
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    write_tasks(new_tasks)
    return {"message": "Tarea eliminada correctamente"}
