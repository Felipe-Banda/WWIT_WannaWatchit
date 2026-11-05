from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional

from schemas import Obra, ObraStatus, ObraUpdate, ObraSearch
from database import engine, SessionLocal
import models

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title = 'WWIT API', version = 'alpha')

# --- ÁREA PÚBLICA --- #
@app.get('/')
def root():
    return {'mensagem': 'WWIT API is running with SQLite!'}

@app.get('/obras', response_model = list[ObraSearch])
def obra_list(db: Session = Depends(get_db)):
    active_db = db.query(models.Obra).filter(models.Obra.ativo == True).all()
    return active_db

@app.get('/obras/buscar', response_model=list[ObraSearch])
def obra_search(titulo: Optional[str] = None, db: Session = Depends(get_db)):
    if not titulo:
        return obra_list(db)
    results = db.query(models.Obra).filter(models.Obra.titulo.ilike(f'%{titulo}%'), models.Obra.ativo == True).all()
    if not results:
        raise HTTPException(status_code=404, detail=f'Nenhum resultado encontrado para o título: {titulo}.')
    return results

@app.get('/obras/{id}', response_model = Obra)
def obra_id_find(id: int, db: Session = Depends(get_db)):
    obra = db.query(models.Obra).filter(models.Obra.id == id, models.Obra.ativo == True).first()
    if not obra:
        raise HTTPException(status_code=404, detail=f'Nenhum resultado encontrado para o id: {id}.')
    return obra

# --- ÁREA RESTRITA --- #
@app.get('/admin/obras', response_model=list[ObraSearch])
def obra_list_admin(db: Session = Depends(get_db)):
    return db.query(models.Obra).all()

@app.post('/admin/obras')
def obra_add(obra: Obra, db: Session = Depends(get_db)):
    nova_obra = models.Obra(
        titulo = obra.titulo,
        sinopse = obra.sinopse,
        autor = obra.autor,
        nota = obra.nota,
        ativo = obra.ativo
    )
    db.add(nova_obra)
    db.commit()
    db.refresh(nova_obra)
    return {'mensagem': f'Obra adicionada com sucesso!',
        'obra': {'id': nova_obra.id, 'titulo': nova_obra.titulo}}

@app.get('/admin/obras/buscar', response_model=list[ObraSearch])
def obra_search_admin(titulo: Optional[str] = None, db: Session = Depends(get_db)):
    if not titulo:
       return obra_list_admin(db)
    results = db.query(models.Obra).filter(models.Obra.titulo.ilike(f'%{titulo}%')).all()
    if not results:
        raise HTTPException(status_code=404, detail=f'Nenhum resultado encontrado para o título: {titulo}.')
    return results

@app.put('/admin/obras/{id}')
def obra_atualizar(id: int, obra_update: ObraUpdate, db: Session = Depends(get_db)):
    obra_db = db.query(models.Obra).filter(models.Obra.id == id).first()
    if not obra_db:
        raise HTTPException(status_code=404, detail=f'Nenhum resultado encontrado para o id: {id}.')

    if obra_update.titulo is not None:
        obra_db.titulo = obra_update.titulo
    if obra_update.sinopse is not None:
        obra_db.sinopse = obra_update.sinopse
    if obra_update.autor is not None:
        obra_db.autor = obra_update.autor
    if obra_update.nota is not None:
        obra_db.nota = obra_update.nota

    db.commit()
    db.refresh(obra_db)
    return {'mensagem': 'Obra atualizada com sucesso!', 'obra': Obra.model_validate(obra_db)}

@app.put('/admin/obras/{id}/status')
def obra_status_set(id: int, status: ObraStatus, db: Session = Depends(get_db)):
    obra_db = db.query(models.Obra).filter(models.Obra.id == id).first()
    if not obra_db:
        raise HTTPException(status_code=404, detail=f'Nenhum resultado encontrado para o id: {id}.')
    
    obra_db.ativo = status.ativo
    db.commit()
    return{'mensagem': f'Status da obra com id {id} atualizado para {"ativo" if status.ativo else "inativo"}.'}
