from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt

from schemas import Obra, ObraStatus, ObraUpdate, ObraSearch, NewUser, Token
from database import engine, SessionLocal
import models

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#--- Configurações de autenticação e segurança ---#
SECRET_KEY = "wwit-super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

app = FastAPI(title = 'WWIT API', version = 'alpha')

# --- ROTAS DE AUTENTICAÇÃO --- #
@app.post("/registro", status_code=status.HTTP_201_CREATED)
def registrar_usuario(user: NewUser, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Nome de usuário já está em uso.")
    
    hashed_password = get_password_hash(user.password)
    novo_usuario = models.User(username=user.username, password=hashed_password)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return {"mensagem": f"Usuário {novo_usuario.username} criado com sucesso!"}

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

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
    obra = db.query(models.Obra).filter(models.Obra.id == id).first()
    if not obra:
        raise HTTPException(status_code=404, detail=f'Nenhum resultado encontrado para o id: {id}.')
    return obra

# --- ÁREA RESTRITA --- #
@app.get('/admin/obras', response_model=list[ObraSearch])
def obra_list_admin(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Obra).all()

@app.post('/admin/obras')
def obra_add(obra: Obra, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
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
def obra_search_admin(titulo: Optional[str] = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not titulo:
       return obra_list_admin(db = db, current_user = current_user)
    results = db.query(models.Obra).filter(models.Obra.titulo.ilike(f'%{titulo}%')).all()
    if not results:
        raise HTTPException(status_code=404, detail=f'Nenhum resultado encontrado para o título: {titulo}.')
    return results

@app.put('/admin/obras/{id}')
def obra_atualizar(id: int, obra_update: ObraUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
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
def obra_status_set(id: int, status: ObraStatus, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    obra_db = db.query(models.Obra).filter(models.Obra.id == id).first()
    if not obra_db:
        raise HTTPException(status_code=404, detail=f'Nenhum resultado encontrado para o id: {id}.')
    
    obra_db.ativo = status.ativo
    db.commit()
    return{'mensagem': f'Status da obra com id {id} atualizado para {"ativo" if status.ativo else "inativo"}.'}
