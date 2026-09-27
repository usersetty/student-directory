from pydantic import BaseModel,Field,EmailStr

class StudentCreate(BaseModel):
    name:str = Field(...,min_length=1)
    email:EmailStr
    course:str=Field(...,min_length=1)
    age:int=Field(...,gt=0)

class StudentResponse(BaseModel):
    id:int
    name:str
    email:str
    course:str
    age:int
    created_at:str