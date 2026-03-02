import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import UploadPanel from './components/UploadPanel';
import QueryPanel from './components/QueryPanel';
import MetricsCards from './components/MetricsCards';
import { getStats } from './api/api';

function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const data = await getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      // Set default stats on error
      setStats({
        total_documents: 0,
        total_chunks: 0,
        queries_processed: 0,
        avg_response_time: 0
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    // Refresh stats every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    
    // Listen for tab switch events
    const handleTabSwitch = (e) => {
      setActiveTab(e.detail);
    };
    window.addEventListener('switchTab', handleTabSwitch);
    
    return () => {
      clearInterval(interval);
      window.removeEventListener('switchTab', handleTabSwitch);
    };
  }, []);

  const handleUploadSuccess = (result) => {
    if (result?.chunks_created) {
      setStats((prev) => ({
        total_documents: (prev?.total_documents || 0) + 1,
        total_chunks: (prev?.total_chunks || 0) + result.chunks_created,
        queries_processed: prev?.queries_processed || 0,
        avg_response_time: prev?.avg_response_time || 0,
      }));
    }

    setLoading(true);
    setTimeout(() => {
      fetchStats();
    }, 500);
  };

  return (
    <div className="min-h-screen flex bg-gradient-dark">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className="flex-1 p-4 md:p-8 lg:p-10 overflow-auto">
        <div className="max-w-7xl mx-auto space-y-8">
          <header className="mb-10 animate-fade-in-up">
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-3">
              <span className="bg-gradient-to-r from-primary-400 via-accent-400 to-primary-400 bg-clip-text text-transparent animate-gradient">
                Agentic RAG System
              </span>
            </h1>
            <p className="text-gray-400 text-sm md:text-base">
              AI-powered financial document analysis with multi-agent reasoning
            </p>
          </header>

          <div className="animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
            <MetricsCards stats={stats} loading={loading} />
          </div>

          <div className="animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
            {activeTab === 'upload' && (
              <UploadPanel onUploadSuccess={handleUploadSuccess} />
            )}

            {activeTab === 'query' && <QueryPanel />}

            {activeTab === 'analytics' && (
              <div className="glass-card p-8 lg:p-12">
                <h2 className="text-2xl md:text-3xl font-bold mb-6 bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">
                  Analytics Dashboard
                </h2>
                <div className="text-center py-16">
                  <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary-500/10 mb-4 float">
                    <svg className="w-10 h-10 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <p className="text-gray-400 text-lg">
                    Analytics features coming soon...
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
