from pydantic import BaseModel
from fastapi import FastAPI,status,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psycopg2 import IntegrityError

from database import get_connection
from schemas import StudentCreate
from ollama import chat
import re
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



# class ChatRequest(BaseModel):
#     message: str

# @app.post("/api/chat")
# def chat(request:ChatRequest):
#     message=request.message.lower().strip()

#     connection = get_connection()
#     try:
#         cursor = connection.cursor()

#         if "how many" in message and "student" in message:
#             cursor.execute("Select  count(*) from students")
#             count=cursor.fetchone()[0]

#             return{
#                 "answer":f"There are {count} students in the directory."

#             }
#         elif "average age" in message:
#             cursor.execute("Select avg(age) from students")
#             average=cursor.fetchone()[0]

#             return {
#                 "answer":f"The average student age is {round(float(average),2)} years."
#             }

#         elif "show all" in message or "list all" in message:
#             cursor.execute(
#                 """
#                 select id,name,email,course,age
#                 from students
#                 order by created_by DESC"""
#             )

#             students=cursor.fetchall()

#             if not students:
#                 return{
#                     "answer":"there are no students in the directory."
#                 }

#             result = []

#             for student in students:
#                 result.append(
#                     f"{student[0]}. {student[1] - student[3]} - Age{student[4]}"
#                 )

#             return {
#                 "answer":"\n".join(result)
#             }
#         elif "data science" in message:
#             cursor.execute(
#                 """
#                 select name
#                 from students
#                 where lower(course)='data science'
#                 """
#             )

#             students=cursor.fetchall()

#             if not students:
#                 return {
#                     "answer": "No students are enrolled in Data Science."
#                 }

#             names = ", ".join(student[0] for student in students)

#             return {
#                 "answer": f"Students studying Data Science: {names}"
#             }
#         else:
#             return {
#                 "answer":"I can answer questions about students,courses and ages."
#             }
#     finally:
#         cursor.close()
#         connection.close()


class ChatRequest(BaseModel):
    message:str

@app.post("/api/chat")
def chat_with_database(request:ChatRequest):
    user_question=request.message.strip()

    if not user_question:
        raise HTTPException(
            status_code=400,
            detail="question can't be empty"
        )

    prompt = f"""
You are an expert PostgreSQL SQL generator.

Database table:

students (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255),
    course VARCHAR(100),
    age INTEGER,
    created_at TIMESTAMP
)

User question:
{user_question}

Generate EXACTLY ONE valid PostgreSQL SELECT query.

IMPORTANT:

- Understand the complete meaning of the user's question.
- Pay attention to words such as:
  "not", "except", "excluding", "without", "other than",
  "less than", "greater than", "above", "below", "before", "after".
- Do NOT simply match keywords.
- Infer the correct SQL condition from the meaning of the question.
- Return ONLY the SQL query.
- Do not provide explanations.
- Do not provide alternative queries.
- Do not use markdown.
- Only use the students table.
- Only SELECT statements are allowed.
- NEVER invent a meaning for an unclear phrase.
- NEVER convert an unknown phrase into an age, course, name, or other field.
- If the user's question cannot be answered using the students table,
  return exactly:
  CLARIFICATION_REQUIRED

SEMANTIC EXAMPLES:
Question:
How many students were not there in how to do?

Return:
CLARIFICATION_REQUIRED

Question:
How many students are not in Data Science?

SQL:
SELECT COUNT(*)
FROM students
WHERE course NOT ILIKE '%Data Science%';

Question:
How many students are older than 21?

SQL:
SELECT COUNT(*)
FROM students
WHERE age > 21;
Question:
How many students are studying Data Science?

SQL:
SELECT COUNT(*) FROM students
WHERE course ILIKE '%Data Science%';

Question:
How many students are NOT studying Data Science?

SQL:
SELECT COUNT(*) FROM students
WHERE course NOT ILIKE '%Data Science%';

Question:
Show students other than Data Science students.

SQL:
SELECT id, name, email, course, age
FROM students
WHERE course NOT ILIKE '%Data Science%';

Question:
How many students are older than 21?

SQL:
SELECT COUNT(*) FROM students
WHERE age > 21;

Question:
Show students who are not older than 21.

SQL:
SELECT id, name, email, course, age
FROM students
WHERE age <= 21;

Question:
Who is the youngest student?

SQL:
SELECT id, name, email, course, age
FROM students
ORDER BY age ASC
LIMIT 1;

Question:
What courses are available?

SQL:
SELECT DISTINCT course
FROM students
ORDER BY course;

Generate exactly ONE query for this question:
{user_question}
"""

    response=chat(
        model="llama3.2:latest",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    sql = response["message"]["content"].strip()
    if sql.strip() == "CLARIFICATION_REQUIRED":
        return {
        "question": user_question,
        "answer": "I'm not sure what you mean. Please specify what you want to know about the students."
    }

# Remove markdown code fences
    sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"```", "", sql, flags=re.IGNORECASE)
    sql = sql.strip()

    # Keep only the first SQL statement
    if ";" in sql:
        sql = sql.split(";")[0].strip() + ";"

    # Remove anything before the first SELECT
    select_position = sql.lower().find("select")

    if select_position == -1:
        raise HTTPException(
            status_code=400,
            detail="The AI did not generate a valid SELECT query."
        )

    sql = sql[select_position:].strip()
    # Reject obviously invalid aggregate queries
    if re.search(r"COUNT\s*\(\s*\*\s*\)", sql, re.IGNORECASE):
        if re.search(r"SELECT\s+COUNT\s*\(\s*\*\s*\)\s*,\s*\*", sql, re.IGNORECASE):
            raise HTTPException(
                status_code=400,
                detail="Invalid SQL generated by the AI."
        )
    if not sql.lower().startswith("select"):
        raise HTTPException(
            status_code=400,
            detail="Only SELECT queries are allowed."
        )

    select_count = len(
    re.findall(r"\bSELECT\b", sql, re.IGNORECASE)
)

    if select_count != 1:
        raise HTTPException(
        status_code=400,
        detail="AI generated multiple SQL queries. Request rejected."
    )

    forbidden=["insert",
               "update",
               "delete",
               "drop",
               "alter",
               "create",
               "truncate",
               "grant",
               "revoke"]

    sql_lower=sql.lower()

    for word in forbidden:
        if re.search(rf"\b{word}\b", sql_lower):
            raise HTTPException(
                status_code=400,
                detail="Unsafe SQL query rejected."
            )

    # Make sure the query only accesses students
    if "students" not in sql_lower:
        raise HTTPException(
            status_code=400,
            detail="Query must use the students table."
        )

    connection = get_connection()

    try:
        cursor=connection.cursor()

        try:
            cursor.execute(sql)
            rows = cursor.fetchall()

        except Exception as e:
            connection.rollback()

            raise HTTPException(
            status_code=400,
            detail=f"Generated SQL could not be executed: {str(e)}")

        columns=[desc[0] for desc in cursor.description]

        results = [
            dict(zip(columns,row))
            for row in rows
        ]
        result_text = str(results)

        answer_prompt = f"""
            You are a helpful assistant for a Student Directory.

            The user asked:
            {user_question}

            The PostgreSQL query returned:
            {result_text}

            Answer the user's question naturally and concisely.

            Rules:
            - Do not mention SQL.
            - Do not mention PostgreSQL.
            - Do not invent information.
            - Use only the provided database result.
            - If the result is a count, clearly state the number.
            - If the result contains students, summarize the students clearly.
            """

        answer_response = chat(
            model="llama3.2:latest",
            messages=[
                {
                    "role": "user",
                    "content": answer_prompt
                }
                ]
            )

        answer = answer_response["message"]["content"].strip()

        return {
    "question": user_question,
    "answer": answer,
    "sql": sql,
    "results": results}

    finally:
        cursor.close()
        connection.close()