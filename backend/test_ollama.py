from ollama import chat

response = chat(
    model="llama3.2:latest",
    messages=[
        {
            "role":"user",
            "content":"convert this to sql for a postgres students table:how many students are there?"
        }
    ]
)

print(response["message"]["content"])