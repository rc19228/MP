import React from 'react';
import { FileText, MessageSquare, TrendingUp, Settings } from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'upload', icon: FileText, label: 'Upload Documents' },
    { id: 'query', icon: MessageSquare, label: 'Ask Questions' },
    { id: 'analytics', icon: TrendingUp, label: 'Analytics' },
  ];

  return (
    <div className="w-64 lg:w-72 glass-card m-4 lg:m-6 p-6 lg:p-8 flex flex-col animate-slide-in">
      <div className="mb-10">
        <h1 className="text-2xl lg:text-3xl font-bold bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent animate-gradient">
          FinanceRAG
        </h1>
        <p className="text-xs lg:text-sm text-gray-400 mt-2">Agentic Financial Analysis</p>
      </div>

      <nav className="flex-1 space-y-3">
        {menuItems.map((item, index) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center space-x-3 px-4 lg:px-5 py-3 lg:py-4 rounded-xl transition-all duration-300 animate-fade-in ${
              activeTab === item.id
                ? 'bg-gradient-to-r from-primary-600 to-primary-500 text-white shadow-lg shadow-primary-500/30 scale-105'
                : 'hover:bg-black/40 text-gray-300 hover:text-white hover:scale-105'
            }`}
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <item.icon size={20} className="flex-shrink-0" />
            <span className="font-medium text-sm lg:text-base">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="mt-auto pt-6 border-t border-white/10">
        <button className="w-full flex items-center space-x-3 px-4 lg:px-5 py-3 lg:py-4 rounded-xl hover:bg-black/40 text-gray-300 hover:text-white transition-all duration-300 hover:scale-105">
          <Settings size={20} className="flex-shrink-0" />
          <span className="font-medium text-sm lg:text-base">Settings</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
