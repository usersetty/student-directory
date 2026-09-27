# Student Directory Management System

A simple Student Directory Management System built using React, FastAPI, and PostgreSQL.

The application allows users to:

- Add students
- View all students
- Edit student details
- Delete students
- Validate student information
- Handle duplicate email addresses
- Persist data in PostgreSQL

## Technologies Used

### Frontend
- React
- Vite
- Axios
- CSS

### Backend
- Python
- FastAPI
- Uvicorn
- psycopg2
- Pydantic

### Database
- PostgreSQL

### Tools
- Git
- GitHub
- FastAPI Swagger

## Project Structure

```text
student-directory/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── schemas.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   └── package.json
│
├── .gitignore
└── README.md
```

## PostgreSQL Database Setup

Create the database:

```sql
CREATE DATABASE studentdb;
```

Connect to the database:

```sql
\c studentdb
```

Create the students table:

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    course VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL CHECK (age > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Insert sample students:

```sql
INSERT INTO students (name, email, course, age) VALUES
('Rahul Kumar', 'rahul@example.com', 'Computer Science', 21),
('Priya Sharma', 'priya@example.com', 'Data Science', 22),
('Arjun Reddy', 'arjun@example.com', 'Information Science', 20),
('Sneha Patil', 'sneha@example.com', 'Electronics', 23),
('Vikram Singh', 'vikram@example.com', 'Mechanical Engineering', 21);
```

## Backend Setup

Go to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
py -3.11 -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=studentdb
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD
```

Run FastAPI:

```bash
python -m uvicorn main:app --reload
```

Backend will run at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

## Frontend Setup

Open another terminal.

Go to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Frontend will run at:

```text
http://localhost:5173
```

## Running the Complete Application

1. Start PostgreSQL.
2. Start the FastAPI backend.
3. Start the React frontend.
4. Open `http://localhost:5173` in a browser.

The application communicates with the backend through REST APIs, and PostgreSQL is the source of truth for student data.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/students` | Get all students |
| POST | `/api/students` | Add a student |
| PUT | `/api/students/{id}` | Update a student |
| DELETE | `/api/students/{id}` | Delete a student |

### HTTP Status Codes

| Status | Meaning |
|---|---|
| 200 | Successful GET/PUT |
| 201 | Student created |
| 204 | Student deleted |
| 404 | Student not found |
| 409 | Duplicate email |
| 422 | Invalid student data |

## Validation

The application validates:

- Name is required
- Email is required
- Course is required
- Email must be unique
- Age must be greater than 0

## Testing

The APIs can be tested using FastAPI Swagger:

```text
http://localhost:8000/docs
```

The following cases should be tested:

- GET students
- POST student
- PUT student
- DELETE student
- Duplicate email
- Invalid student data
- Non-existing student ID

## Assumptions and Limitations

- PostgreSQL must be installed and running locally.
- Database credentials are stored in `.env`.
- `.env` is not committed to GitHub.
- The application is intended for local development and demonstration.
- Authentication and user management are not included.

## GitHub

Repository name:

```text
student-directory
```

Before pushing to GitHub, make sure the following are excluded:

- `.env`
- `venv/`
- `.venv/`
- `__pycache__/`
- `node_modules/`
- `dist/`
