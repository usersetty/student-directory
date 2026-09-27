from fastapi import FastAPI,status,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psycopg2 import IntegrityError

from database import get_connection
from schemas import StudentCreate

app =FastAPI(title="student directory API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/students")
def get_students():
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("""
        SELECT * FROM STUDENTS""")

        students = cursor.fetchall()

        return [{
            "id":student[0],
            "name":student[1],
            "email":student[2],
            "course":student[3],
            "age":student[4],
            "created_at":student[5]
        }
        for student in students]

    finally:
        cursor.close()
        connection.close()


@app.post("/api/students",status_code=status.HTTP_201_CREATED)
def create_student(student:StudentCreate):
    connection = get_connection()

    try:
        cursor=connection.cursor()

        cursor.execute("""
        INSERT INTO STUDENTS(name,email,course,age)
        values (%s,%s,%s,%s)
        RETURNING id,name,email,course,age,created_at""",
        (
            student.name,
            student.email,
            student.course,
            student.age
        )
        )
        new_student = cursor.fetchone()
        connection.commit()

        return {
            "id":new_student[0],
            "name":new_student[1],
            "email":new_student[2],
            "course":new_student[3],
            "age":new_student[4],
            "created_at":new_student[5] 
        }


    except IntegrityError:
        connection.rollback()

        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            details="Email already exists"
        )

    finally:
        cursor.close()
        connection.close()



@app.put("/api/students/{student_id}")
def update_student(student_id:int,student:StudentCreate):
    connection=get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE STUDENTS
            SET name=%s,
            email=%s,
            course=%s,
            age=%s
            where id=%s
            RETURNING id,name,email,course,age,created_at""",
            (student.name,
             student.email,
             student.course,
             student.age,
             student_id)
        )

        update_student=cursor.fetchone()
        if update_student is None:
            connection.rollback()

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="student not found"
            )

        connection.commit()

        return {
            "id":update_student[0],
            "name":update_student[1],
            "email":update_student[2],
            "course":update_student[3],
            "age":update_student[4],
            "created_at":update_student[5]
        }

    except IntegrityError:
        connection.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    finally:
        cursor.close()
        connection.close()


@app.delete("/api/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM students
            WHERE id = %s
            """,
            (student_id,)
        )

        if cursor.rowcount == 0:
            connection.rollback()

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )

        connection.commit()

    finally:
        cursor.close()
        connection.close()