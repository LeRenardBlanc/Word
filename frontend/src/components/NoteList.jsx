import React from 'react';

const NoteList = ({ notes, onSelectNote, selectedNoteId, onDeleteNote }) => {
  return (
    <div className="w-80 border-r border-gray-700 bg-gray-900 flex flex-col h-full">
      <div className="p-3 border-b border-gray-800 bg-gray-900 z-10">
        <span className="text-gray-400 text-sm font-medium">{notes.length} notes</span>
      </div>
      <div className="overflow-y-auto flex-1 custom-scrollbar">
        {notes.length === 0 ? (
           <div className="p-4 text-center text-gray-500 text-sm mt-10">Aucune note trouvée.</div>
        ) : (
          notes.map(note => (
            <div
              key={note.id}
              className={`group p-4 border-b border-gray-800 cursor-pointer transition-all hover:bg-gray-800 relative
                ${note.id === selectedNoteId ? 'bg-gray-800 border-l-4 border-l-indigo-500' : 'border-l-4 border-l-transparent'}`}
              onClick={() => onSelectNote(note)}
            >
              <div className="flex justify-between items-start mb-1">
                <h4 className={`font-semibold text-sm truncate pr-6 ${note.id === selectedNoteId ? 'text-white' : 'text-gray-300'}`}>
                  {note.title || 'Sans titre'}
                </h4>
                <span className="text-xs text-gray-500 whitespace-nowrap">
                   {new Date(note.updated_at || note.created_at).toLocaleDateString()}
                </span>
              </div>

              <p className="text-xs text-gray-500 line-clamp-2 h-8">
                  {note.content ? note.content.replace(/<[^>]+>/g, '') : 'Pas de contenu...'}
              </p>

              <button
                className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 p-1 text-gray-500 hover:text-red-400 hover:bg-gray-700 rounded transition-all"
                onClick={(e) => {
                    e.stopPropagation();
                    if(window.confirm('Supprimer cette note ?')) onDeleteNote(note.id);
                }}
                title="Supprimer"
              >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default NoteList;
