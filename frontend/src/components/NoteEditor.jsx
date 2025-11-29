import React, { useState, useEffect } from 'react';
import ReactQuill from 'react-quill';
import { summarizeText, generateFlashcards } from '../api';

const NoteEditor = ({ note, onUpdate }) => {
  const [title, setTitle] = useState(note.title);
  const [content, setContent] = useState(note.content || '');
  const [aiResult, setAiResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showAiPanel, setShowAiPanel] = useState(false);

  useEffect(() => {
    setTitle(note.title);
    setContent(note.content || '');
    setAiResult(null);
    setShowAiPanel(false);
  }, [note]);

  const handleBlur = () => {
    onUpdate(note.id, { title, content });
  }

  const handleSummarize = async () => {
      setLoading(true);
      setShowAiPanel(true);
      try {
          const text = content.replace(/<[^>]+>/g, ''); 
          if(text.length < 50) {
              setAiResult({ type: 'error', data: "Texte trop court pour être résumé."});
              return;
          }
          const result = await summarizeText(text);
          setAiResult({ type: 'summary', data: result.summary });
      } catch (e) {
          setAiResult({ type: 'error', data: "Erreur lors du résumé."});
      } finally {
          setLoading(false);
      }
  };

  const handleFlashcards = async () => {
      setLoading(true);
      setShowAiPanel(true);
      try {
          const text = content.replace(/<[^>]+>/g, '');
          if(text.length < 50) {
            setAiResult({ type: 'error', data: "Texte trop court pour générer des flashcards."});
            return;
          }
          const result = await generateFlashcards(text);
          setAiResult({ type: 'flashcards', data: result.flashcards });
      } catch (e) {
          setAiResult({ type: 'error', data: "Erreur lors de la génération."});
      } finally {
          setLoading(false);
      }
  }

  // Quill modules configuration
  const modules = {
    toolbar: [
      [{ 'header': [1, 2, 3, false] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      ['blockquote', 'code-block'],
      ['clean']
    ],
  };

  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 relative">
      {/* Header */}
      <div className="flex items-center justify-between px-8 py-4 border-b border-gray-700 bg-gray-900">
        <input 
          type="text" 
          className="text-2xl font-bold bg-transparent border-none focus:outline-none focus:ring-0 w-full text-white placeholder-gray-500"
          value={title} 
          onChange={(e) => setTitle(e.target.value)}
          onBlur={handleBlur}
          placeholder="Titre de la note..."
        />
        <div className="flex items-center space-x-2">
            <button 
                onClick={handleBlur} 
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
                Sauvegarder
            </button>
        </div>
      </div>
      
      {/* Editor & AI Panel Container */}
      <div className="flex-1 flex overflow-hidden">
          {/* Main Editor */}
          <div className="flex-1 flex flex-col relative">
             <ReactQuill 
                theme="snow" 
                value={content} 
                onChange={setContent}
                onBlur={handleBlur}
                modules={modules}
                className="flex-1 overflow-y-auto"
                placeholder="Commencez à écrire..."
            />
          </div>

          {/* AI Sidebar (Toggleable) */}
          <div className={`w-80 bg-gray-900 border-l border-gray-700 flex flex-col transition-all duration-300 ${showAiPanel ? 'translate-x-0' : 'translate-x-full hidden'}`}>
              <div className="p-4 border-b border-gray-700 flex justify-between items-center">
                  <h3 className="font-bold text-indigo-400 flex items-center gap-2">
                      🤖 Assistant IA
                  </h3>
                  <button onClick={() => setShowAiPanel(false)} className="text-gray-400 hover:text-white">&times;</button>
              </div>
              <div className="p-4 flex-1 overflow-y-auto">
                  {loading ? (
                      <div className="flex flex-col items-center justify-center h-40 space-y-4">
                          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
                          <p className="text-sm text-gray-400">L'IA réfléchit...</p>
                      </div>
                  ) : aiResult ? (
                      <div className="space-y-4">
                          <h4 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
                              {aiResult.type === 'summary' ? 'Résumé' : aiResult.type === 'error' ? 'Erreur' : 'Flashcards'}
                          </h4>
                          
                          {aiResult.type === 'summary' && (
                              <div className="bg-gray-800 p-3 rounded-lg text-sm leading-relaxed border border-gray-700">
                                  {aiResult.data}
                              </div>
                          )}

                          {aiResult.type === 'flashcards' && (
                              <div className="space-y-3">
                                  {aiResult.data.map((card, i) => (
                                      <div key={i} className="bg-gray-800 p-3 rounded-lg border border-gray-700 text-sm">
                                          {card}
                                      </div>
                                  ))}
                              </div>
                          )}
                          
                           {aiResult.type === 'error' && (
                              <div className="text-red-400 text-sm">
                                  {aiResult.data}
                              </div>
                          )}
                      </div>
                  ) : (
                      <div className="text-center text-gray-500 mt-10 text-sm">
                          Sélectionnez une action ci-dessous pour lancer l'analyse.
                      </div>
                  )}
              </div>
              <div className="p-4 border-t border-gray-700 space-y-2">
                  <button 
                    onClick={handleSummarize} 
                    className="w-full bg-gray-800 hover:bg-gray-700 border border-gray-600 text-white py-2 rounded-md text-sm transition-colors flex items-center justify-center gap-2"
                  >
                      📄 Résumer
                  </button>
                  <button 
                    onClick={handleFlashcards} 
                    className="w-full bg-gray-800 hover:bg-gray-700 border border-gray-600 text-white py-2 rounded-md text-sm transition-colors flex items-center justify-center gap-2"
                  >
                      🗂️ Générer Flashcards
                  </button>
              </div>
          </div>

           {/* Floating AI Button (Visible when panel is hidden) */}
           {!showAiPanel && (
              <button 
                  onClick={() => setShowAiPanel(true)}
                  className="absolute bottom-8 right-8 bg-indigo-600 hover:bg-indigo-700 text-white p-4 rounded-full shadow-lg transition-transform hover:scale-110 z-50"
                  title="Ouvrir l'assistant IA"
              >
                  🤖
              </button>
           )}
      </div>
    </div>
  );
};

export default NoteEditor;
