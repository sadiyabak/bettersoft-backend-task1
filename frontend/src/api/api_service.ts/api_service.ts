import axios from "axios";

// ✅ Create a base instance of Axios
const api = axios.create({
  baseURL: "http://localhost:5000/api", // change this to your backend URL if needed
  headers: {
    "Content-Type": "application/json",
  },
});

// ✅ Example CRUD API calls
export const getComments = async (taskId: string) => {
  return await api.get(`/comments/${taskId}`);
};

export const addComment = async (taskId: string, commentData: any) => {
  return await api.post(`/comments/${taskId}`, commentData);
};

export const updateComment = async (commentId: string, updatedData: any) => {
  return await api.put(`/comments/${commentId}`, updatedData);
};

export const deleteComment = async (commentId: string) => {
  return await api.delete(`/comments/${commentId}`);
};

export default api;
