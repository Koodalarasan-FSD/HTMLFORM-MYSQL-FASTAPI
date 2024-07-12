from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

# Database connection function
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="html-db-fastapi"
    )
    return conn

# To Run/Execute the python file - Run these command:  uvicorn app:app --reload
# Note: In above first app is name of these project file and second app is command to run these project.

# Templates directory
templates = Jinja2Templates(directory="templates")

# Route to render index.html
@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    """
    In FastAPI, rendering templates directly isn't supported out of the box because it's primarily 
    designed for building APIs rather than rendering HTML templates. However, you can achieve 
    a similar effect by using FastAPI alongside a template rendering engine like Jinja2
    """
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint to handle form submission and store data
@app.post('/submit-form/')
async def submit_form(name: str = Form(...), email: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, email) VALUES (%s, %s)', (name, email))
    conn.commit()
    cursor.close()
    conn.close()
    return RedirectResponse(url='/',status_code=303)

# API endpoint to retrieve users
@app.get('/api/users/')
async def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

# Pydantic model for updating user
class UpdateUser(BaseModel):
    name: str = None
    email: str = None

# API endpoint to update a user
@app.put('/api/users/{id}')
async def update_user(id: int, user: UpdateUser):
    conn = get_db_connection()
    cursor = conn.cursor()
    if not user.name and not user.email:
        raise HTTPException(status_code=400, detail="Name and Email cannot both be empty")

    if user.name and user.email:
        cursor.execute('UPDATE users SET name = %s, email = %s WHERE id = %s', (user.name, user.email, id))
    elif user.name:
        cursor.execute('UPDATE users SET name = %s WHERE id = %s', (user.name, id))
    elif user.email:
        cursor.execute('UPDATE users SET email = %s WHERE id = %s', (user.email, id))
    
    conn.commit()
    cursor.close()
    conn.close()
    return RedirectResponse(url='/', status_code=303)

# Running the app with uvicorn server
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000, debug=True)
