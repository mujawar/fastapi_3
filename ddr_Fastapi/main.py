from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker
from crud import CRUD
from db import engine
from schemas import NoteModel, NoteCreateModel
from http import HTTPStatus
from typing import List
from models import Note
import uuid

## JWT TOKEN IMPLMENTAION##
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
# Define a security scheme using OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
## JWT TOKEN IMPLMENTAION##

app = FastAPI(
    title="Noted API", description="This is a simple note taking service", docs_url="/"
)

#create an async session object for CRUD
session = async_sessionmaker(bind=engine, expire_on_commit=False)

db = CRUD()


@app.get("/notes", response_model=List[NoteModel])
async def get_all_notes():
    """API endpoint for listing all note resources
    """
    notes = await db.get_all(session)

    return notes


@app.post("/notes", status_code=HTTPStatus.CREATED)
async def create_note(note_data: NoteCreateModel):
    """API endpoint for creating a note resource

    7890

    Args:
        note_data (NoteCreateModel): data for creating a note using the note schema

    Returns:
        dict: note that has been created
    """
    new_note = Note(
        id=str(uuid.uuid4()), 
        title=note_data.title, 
        content=note_data.content
    )

    note = await db.add(session, new_note)

    return note


@app.get("/note/{note_id}")
async def get_note_by_id(note_id):
    """API endpoint for retrieving a note by its ID

    Args:
        note_id (str): the ID of the note to retrieve

    Returns:
        dict: The retrieved note
    """
    note = await db.get_by_id(session, note_id)

    return note


@app.patch("/note/{note_id}")
async def update_note(note_id: str, data: NoteCreateModel):
    """Update by ID

    Args:
        note_id (str): ID of note to update
        data (NoteCreateModel): data to update note

    Returns:
        dict: the updated note
    """
    note = await db.update(
        session, 
        note_id, 
        data={"title": data.title, "content": data.content}
    )

    return note


@app.delete("/note/{note_id}")
async def delete_note(note_id) -> None:
    """Delete note by id

    Args:
        note_id (str): ID of note to delete

    """
    note = await db.get_by_id(session, note_id)

    result = await db.delete(session, note)

    return result







@app.post("/login")
async def login(username: str, password: str):
    # Replace this with your actual user authentication logic
    print("username",username)
    print("password",password)
    if username == 'arif' and password == 'arif@123':
        token = create_jwt_token(username)
        return {"token": token, "username": username, "status": 200}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# Helper function to create JWT token
def create_jwt_token(username: str):
    # Replace this with your actual JWT token creation logic
    from datetime import datetime, timedelta
    

    expiration_time = datetime.utcnow() + timedelta(minutes=30)
    token_data = {"sub": username, "exp": expiration_time}
    token = jwt.encode(token_data, SECRET_KEY, ALGORITHM)
    return token


# Function to verify and decode the JWT token
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return {"username": username}



@app.get("/unprotected")
async def unprotected():
    return {"message": "Anyone can see this"}

@app.get("/protected")
async def protected(current_user: dict = Depends(get_current_user)):
    return {"message": "This is available for people with a valid token", "current_user": current_user}
