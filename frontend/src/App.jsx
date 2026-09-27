import { useEffect, useState } from "react";
import {
  getStudents,
  createStudent,
  updateStudent,
  deleteStudent,
  sendChatMessage
} from "./api";

import "./App.css";

function App() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [chatSQL, setChatSQL] = useState("");

  const [form, setForm] = useState({
    name: "",
    email: "",
    course: "",
    age: ""
  });

  const [editingId, setEditingId] = useState(null);
  const [chatMessage, setChatMessage] = useState("");
  const [chatResponse, setChatResponse] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  const fetchStudents = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getStudents();
      setStudents(data);
    } catch (err) {
      setError("Failed to load students.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, []);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  const validateForm = () => {
    if (!form.name.trim()) {
      setError("Name is required.");
      return false;
    }

    if (!form.email.trim()) {
      setError("Email is required.");
      return false;
    }

    if (!form.course.trim()) {
      setError("Course is required.");
      return false;
    }

    if (!form.age || Number(form.age) <= 0) {
      setError("Age must be greater than 0.");
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");

    if (!validateForm()) {
      return;
    }

    try {
      const studentData = {
        name: form.name,
        email: form.email,
        course: form.course,
        age: Number(form.age)
      };

      if (editingId) {
        await updateStudent(editingId, studentData);
      } else {
        await createStudent(studentData);
      }

      resetForm();
      await fetchStudents();

    } catch (err) {
      if (err.response?.status === 409) {
        setError("Email already exists.");
      } else {
        setError("Failed to save student.");
      }
    }
  };

  const handleEdit = (student) => {
    setForm({
      name: student.name,
      email: student.email,
      course: student.course,
      age: student.age
    });

    setEditingId(student.id);
    setError("");
  };

  const handleDelete = async (id) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this student?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");

      await deleteStudent(id);
      await fetchStudents();

    } catch (err) {
      setError("Failed to delete student.");
    }
  };

  const resetForm = () => {
    setForm({
      name: "",
      email: "",
      course: "",
      age: ""
    });

    setEditingId(null);
  };


  const handleChat = async (e) => {
    e.preventDefault();

    if (!chatMessage.trim()) {
      return;
    }

    try {
      setChatLoading(true);
      setChatResponse("");
      const data = await sendChatMessage(chatMessage);

      setChatResponse(data.answer);
      setChatSQL(data.sql);


    }
    catch (err) {

      setChatResponse("Sorry i could process your question")
      print(err)
    }
    finally {
      setChatLoading(false);
    }
  }
  return (
    <div className="container">

      <h1>Student Directory Management System</h1>
      <p className="subtitle">Manage student records easily</p>

      <form onSubmit={handleSubmit} className="student-form">

        <input
          type="text"
          name="name"
          placeholder="Name"
          value={form.name}
          onChange={handleChange}
        />

        <input
          type="email"
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
        />

        <input
          type="text"
          name="course"
          placeholder="Course"
          value={form.course}
          onChange={handleChange}
        />

        <input
          type="number"
          name="age"
          placeholder="Age"
          value={form.age}
          onChange={handleChange}
        />

        <button type="submit">
          {editingId ? "Update Student" : "Save"}
        </button>

        {editingId && (
          <button
            type="button"
            onClick={resetForm}
          >
            Cancel
          </button>
        )}

      </form>

      {error && (
        <p className="error">
          {error}
        </p>
      )}

      {loading ? (
        <p>Loading...</p>
      ) : students.length === 0 ? (
        <p>No students yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Course</th>
              <th>Age</th>
              <th>Edit</th>
              <th>Delete</th>
            </tr>
          </thead>

          <tbody>
            {students.map((student) => (
              <tr key={student.id}>
                <td>{student.id}</td>
                <td>{student.name}</td>
                <td>{student.email}</td>
                <td>{student.course}</td>
                <td>{student.age}</td>

                <td>
                  <button
                    onClick={() => handleEdit(student)}
                  >
                    Edit
                  </button>
                </td>

                <td>
                  <button
                    onClick={() => handleDelete(student.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <div className="chatbot">

        <h2>Student Assistant</h2>

        <p className="chat-help">
          Ask questions about students, courses, and ages.
        </p>

        <form onSubmit={handleChat} className="chat-form">

          <input
            type="text"
            placeholder="Ask something..."
            value={chatMessage}
            onChange={(e) => setChatMessage(e.target.value)}
          />

          <button type="submit" disabled={chatLoading}>
            {chatLoading ? "Thinking..." : "Ask"}
          </button>

        </form>

        {chatResponse && (
          <div className="chat-response">
            {chatResponse}
          </div>
        )}
        {
          chatSQL && (
            <details className="sql-section">
              <summary>Show generated SQL</summary>
              <pre>{chatSQL}</pre>
            </details>
          )
        }

      </div>
    </div>


  );
}

export default App;