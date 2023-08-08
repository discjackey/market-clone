from fastapi import FastAPI,UploadFile,Form,Response,Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from typing import Annotated
import sqlite3

con = sqlite3.connect('index.db', check_same_thread=False)
cur = con.cursor()

cur.execute(f"""
            CREATE TABLE IF NOT EXISTS items (
	            id INTEGER PRIMARY KEY,
	            title TEXT NOT NULL,
	            image BLOB,
	            price INTEGER NOT NULL,
	            description TEXT,
	            place TEXT NOT NULL,
	            createdAt INTEGER NOT NULL
            );""")
    
app = FastAPI()

# 어떻게 액세스코딩을 인코딩할지 정해주는 것 (해시는 디코딩이 안되는데 JWT는 가능)
SECRET = 'super-coding'
manager = LoginManager(SECRET, '/login')

@manager.user_loader()
def query_user(data):
    WHERE_STATEMENTS = f'id="{data}"'
    if type(data) == dict:
        WHERE_STATEMENTS = f'''id="{data['id']}"'''
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    user = cur.execute(f"""
                       SELECT * FROM users WHERE {WHERE_STATEMENTS}
                       """).fetchone()
    return user

@app.post('/login')
def login(id:Annotated[str,Form()], 
           password:Annotated[str,Form()]):
    user = query_user(id)
    print(user)
    
    if not user:
        raise InvalidCredentialsException
    elif password != user['password']:
        raise InvalidCredentialsException
    
    access_token = manager.create_access_token(data={
     'sub': {
        'id': user['id'],
        'name': user['name'],
        'email': user['email']
        }
    });
    return {'access_token':access_token}

@app.post('/signup')
def signup(id:Annotated[str,Form()], 
           password:Annotated[str,Form()],
           name:Annotated[str,Form()],
           email:Annotated[str,Form()]):
    cur.execute(f"""
                INSERT INTO users(id, name, email, password)
                VALUES ('{id}','{name}','{email}','{password}')
                """)
    con.commit()
    print(id, password, name, email)
    return '200'

@app.post('/items')
async def create_item(image:UploadFile,
                title:Annotated[str,Form()],
                price:Annotated[str,Form()],
                description: Annotated[str,Form()],
                place: Annotated[str,Form()],
                createdAt: Annotated[str,Form()],
                user=Depends(manager)):
    
    image_bytes = await image.read()
    cur.execute(f"""
                INSERT INTO items(title,image,price,description,place,createdAt)
                VALUES ('{title}', '{image_bytes.hex()}','{price}','{description}','{place}','{createdAt}')
                """)
    con.commit()
    return '200'

@app.get('/items')
async def get_items(user=Depends(manager)):
    # 컬럼명도 같이 가져오는 문법
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute(f"""
                       SELECT * FROM items
                       """).fetchall()
    return JSONResponse(jsonable_encoder(
        dict(row) for row in rows
        ))
   
@app.get('/images/{item_id}')    
async def get_image(item_id):
    cur = con.cursor()
    image_bytes = cur.execute(f"""
                              SELECT image FROM items WHERE id ={item_id}
                              """).fetchone()[0]
    return Response(content=bytes.fromhex(image_bytes), media_type='image/*')

app.mount("/", StaticFiles(directory="frontend", html=True), name = "frontend")

