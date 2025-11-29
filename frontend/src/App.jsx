import React, { useState, useEffect } from 'react';
import NoteList from './components/NoteList';
import NoteEditor from './components/NoteEditor';
import Sidebar from './components/Sidebar';
import { getNotes, createNote, updateNote, deleteNote } from './api';

function App() {
  const [notes, setNotes] = useState([]);
  const [selectedNote, setSelectedNote] = useState(null);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    try {
      const data = await getNotes();
      setNotes(data);
    } catch (error) {
      console.error("Failed to fetch notes", error);
    }
  };

  const handleSelectNote = (note) => {
    setSelectedNote(note);
  };

  const handleCreateNote = async () => {
    try {
      const newNote = await createNote({ title: "Nouvelle Note", content: "", folder: "General" });
      setNotes([newNote, ...notes]);
      setSelectedNote(newNote);
    } catch (error) {
      console.error("Failed to create note", error);
    }
  };

  const handleUpdateNote = async (id, updatedData) => {
    try {
      const updatedNote = await updateNote(id, updatedData);
      setNotes(notes.map(n => n.id === id ? updatedNote : n));
      if (selectedNote && selectedNote.id === id) {
          setSelectedNote(updatedNote);
      }
    } catch (error) {
      console.error("Failed to update note", error);
    }
  };

  const handleDeleteNote = async (id) => {
      try {
          await deleteNote(id);
          setNotes(notes.filter(n => n.id !== id));
          if (selectedNote && selectedNote.id === id) {
              setSelectedNote(null);
          }
      } catch (error) {
          console.error("Failed to delete note", error);
      }
  }

  const filteredNotes = Array.isArray(notes) ? notes.filter(note => 
    note.title.toLowerCase().includes(filter.toLowerCase()) || 
    (note.content && note.content.toLowerCase().includes(filter.toLowerCase()))
  ) : [];

  return (
    <div className="flex h-screen bg-gray-900 text-white font-sans overflow-hidden">
      <Sidebar 
        onSearch={setFilter} 
        onCreateNote={handleCreateNote} 
      />
      
      <div className="flex-1 flex overflow-hidden">
        <NoteList 
          notes={filteredNotes} 
          onSelectNote={handleSelectNote} 
          selectedNoteId={selectedNote?.id}
          onDeleteNote={handleDeleteNote}
        />
        
        <main className="flex-1 flex flex-col bg-gray-800 relative">
          {selectedNote ? (
            <NoteEditor 
              note={selectedNote} 
              onUpdate={handleUpdateNote} 
            />
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <h3 className="text-2xl font-bold mb-2">Bienvenue</h3>
                <p>Sélectionnez une note ou créez-en une nouvelle pour commencer.</p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
