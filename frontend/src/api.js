import axios from "axios";

const API_URL = "http://localhost:8000/api/students";
export const getStudents = async()=>{
    const response= await axios.get(API_URL);
    return response.data;
}


export const createStudent = async(student)=>{
    const response = await axios.post(API_URL,student);
    return response.data;

}

export const updateStudent = async(id,student)=>{
    const response=await axios.put(`${API_URL}/${id}`,student);
    return response.data;
}

export const deleteStudent = async(id)=>{
    await axios.delete(`${API_URL}/${id}`);
}

export const sendChatMessage = async(message)=>{
    const response= await axios.post(
        "http://localhost:8000/api/chat",
        {
            message:message
        }
    );
    return response.data;
}