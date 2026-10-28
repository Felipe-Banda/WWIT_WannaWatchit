from fastapi import FastAPI, HTTPException
from typing import Optional
from schemas import Obra, ObraStatus, ObraUpdate, ObraSearch

app = FastAPI(title = 'WWIT API', version = 'alpha')
fake_db = []

# --- ÁREA PÚBLICA --- #
@app.get('/')
def root():
    return {'mensagem': 'WWIT API is running!'}

@app.get('/obras')
def obra_list():
    active_db = [obra for obra in fake_db if obra.ativo]
    return active_db

@app.get('/obras/buscar', response_model=list[ObraSearch])
def obra_search(titulo: Optional[str] = None):
    if not titulo:
        return obra_list()
    results = [obra for obra in fake_db
        if titulo.lower() in obra.titulo.lower() and obra.ativo]
    if not results:
        raise HTTPException(status_code=404, detail=f'Nenhum resultado encontrado para o título: {titulo}.')
    return results

@app.get('/obras/{id}')
def obra_id_find(id: int):
    for obra in fake_db:
        if obra.id == id and obra.ativo:
            return obra
    else:
        raise HTTPException(status_code=404, detail=f'Nenhum resultado encontrado para o id: {id}.')


# --- ÁREA RESTRITA --- #
@app.get('/admin/obras', response_model=list[ObraSearch])
def obra_list_admin():
    return fake_db

@app.post('/admin/obras')
def obra_add(obra: Obra):
    for item in fake_db:
        if item.id == obra.id:
            raise HTTPException(status_code=400, detail=f'O id {obra.id} já está em uso para {item.titulo}.')
    fake_db.append(obra)
    return {'mensagem': f'Obra adicionada com sucesso!',
        'obra': {'id': obra.id, 'titulo': obra.titulo}}

@app.get('/admin/obras/buscar')
def obra_search_admin(titulo: Optional[str] = None):
    if not titulo:
       return obra_list_admin()
    results = [obra for obra in fake_db if titulo.lower() in obra.titulo.lower()]
    if not results:
        raise HTTPException(status_code=404, detail=f'Nenhum resultado encontrado para o título: {titulo}.')
    return results

@app.put('/admin/obras/{id}')
def obra_atualizar(id: int, obra_update: ObraUpdate):
    for obra in fake_db:
        if obra.id == id:
            if obra_update.titulo is not None:
                obra.titulo = obra_update.titulo
            if obra_update.sinopse is not None:
                obra.sinopse = obra_update.sinopse
            if obra_update.autor is not None:
                obra.autor = obra_update.autor
            if obra_update.nota is not None:
                obra.nota = obra_update.nota
            return {'mensagem': 'Obra atualizada com sucesso!',
                'obra': obra}
    raise HTTPException(status_code=404, detail=f'Nenhum resultado encontrado para o id: {id}.')

@app.put('/admin/obras/{id}/status')
def obra_status_set(id: int, status: ObraStatus):
    for obra in fake_db:
        if obra.id == id:
            obra.ativo = status.ativo
            return {'mensagem': f'Status da obra com id {id} atualizado para {status.ativo}.'}
    raise HTTPException(status_code=404, detail=f'Nenhum resultado encontrado para o id: {id}.')