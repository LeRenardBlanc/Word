import React, { useEffect, useState } from 'react';
import { getFolders, getTags } from '../api';

const Sidebar = ({ onSearch, onCreateNote }) => {
  const [folders, setFolders] = useState([]);
  const [tags, setTags] = useState([]);

  useEffect(() => {
    // Poll for updates or just load once
    const fetchData = async () => {
        try {
            const f = await getFolders();
            const t = await getTags();
            setFolders(f);
            setTags(t);
        } catch (e) { console.error(e); }
    }
    fetchData();
  }, []);

  return (
    <div className="w-64 bg-gray-950 flex flex-col border-r border-gray-800">
      <div className="p-4 border-b border-gray-800">
        <h2 className="text-xl font-bold text-indigo-400 mb-4 flex items-center gap-2">
          <span>📘</span> Smart Notes
        </h2>
        <button
          onClick={onCreateNote}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <span>+</span> Nouvelle Note
        </button>
      </div>

      <div className="p-4">
        <input
          type="text"
          placeholder="Rechercher..."
          className="w-full bg-gray-900 border border-gray-700 text-gray-300 rounded-md py-2 px-3 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          onChange={(e) => onSearch(e.target.value)}
        />
      </div>

      <div className="flex-1 overflow-y-auto px-2 py-2">
        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 px-2">Dossiers</div>
        <div className="space-y-1">
          <div className="flex items-center px-2 py-2 text-sm font-medium rounded-md bg-gray-800 text-white cursor-pointer">
            📁 Toutes les notes
          </div>
          {Array.isArray(folders) && folders.map(f => (
              f !== 'General' && (
                <div key={f} className="flex items-center px-2 py-2 text-sm font-medium rounded-md text-gray-400 hover:bg-gray-800 hover:text-white cursor-pointer transition-colors">
                    📁 {f}
                </div>
              )
          ))}
        </div>

        <div className="mt-8 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 px-2">Tags</div>
        <div className="space-y-1">
             {Array.isArray(tags) && tags.length > 0 ? tags.map(t => (
                 <div key={t} className="flex items-center px-2 py-1 text-sm font-medium rounded-md text-gray-400 hover:bg-gray-800 hover:text-white cursor-pointer transition-colors">
                     # {t}
                 </div>
             )) : (
                 <div className="px-2 py-1 text-sm text-gray-500 italic">Aucun tag</div>
             )}
        </div>
      </div>

      <div className="p-4 border-t border-gray-800 text-xs text-gray-500">
        v1.0.0 • Local AI
      </div>
    </div>
  );
};

export default Sidebar;
