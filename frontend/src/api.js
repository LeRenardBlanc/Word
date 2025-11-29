import axios from 'axios';

const API_URL = '/api'; // Proxied by Vite

export const getNotes = async () => {
  const response = await axios.get(`${API_URL}/notes/`);
  return response.data;
};

export const getNote = async (id) => {
  const response = await axios.get(`${API_URL}/notes/${id}`);
  return response.data;
};

export const createNote = async (note) => {
  const response = await axios.post(`${API_URL}/notes/`, note);
  return response.data;
};

export const updateNote = async (id, note) => {
  const response = await axios.put(`${API_URL}/notes/${id}`, note);
  return response.data;
};

export const deleteNote = async (id) => {
  const response = await axios.delete(`${API_URL}/notes/${id}`);
  return response.data;
};

export const summarizeText = async (text) => {
    const response = await axios.post(`${API_URL}/ai/summarize`, { text });
    return response.data;
};

export const generateFlashcards = async (text) => {
    const response = await axios.post(`${API_URL}/ai/flashcards`, { text });
    return response.data;
};

export const getFolders = async () => {
    const response = await axios.get(`${API_URL}/folders/`);
    return response.data.folders;
};

export const getTags = async () => {
    const response = await axios.get(`${API_URL}/tags/`);
    return response.data.tags;
};
