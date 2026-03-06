import React, { useState, useEffect } from 'react';
import { Send, Sparkles, Loader } from 'lucide-react';
import { askQuery } from '../api/api';
import ResultDisplay from './ResultDisplay';
import AgentWorkflow from './AgentWorkflow';

const QueryPanel = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [workflowData, setWorkflowData] = useState(null);
  const [currentAgent, setCurrentAgent] = useState(null);

  const exampleQueries = [
    "What is the company's revenue growth over the past 3 years?",
    "Analyze the company's debt-to-equity ratio",
    "What are the key risk factors mentioned?",
    "Summarize the cash flow trends",
  ];

  // Animate through agents during loading
  useEffect(() => {
    if (!loading) {
      setCurrentAgent(null);
      return;
    }

    const agents = ['planner', 'retriever', 'analyzer', 'generator', 'critic'];
    let agentIndex = 0;
    
    // Start with planner
    setCurrentAgent(agents[0]);
    
    // Cycle through agents every 2 seconds
    const interval = setInterval(() => {
      agentIndex = (agentIndex + 1) % agents.length;
      setCurrentAgent(agents[agentIndex]);
    }, 2000);

    return () => clearInterval(interval);
  }, [loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    setResult(null);
    setWorkflowData(null);

    try {
      const response = await askQuery(query);
      
      // Check if backend returned an error status
      if (response.status === 'error') {
        setResult({
          error: true,
          message: response.executive_summary || 'Failed to process query. Please try again.',
        });
        return;
      }
      
      setResult(response);
      
      // Simulate workflow data for visualization
      // In a real implementation, the backend would send this data
      setWorkflowData({
        planner: { completed: true },
        retriever: { completed: true },
        analyzer: { completed: true },
        generator: { completed: true },
        critic: { completed: true },
        confidence: response.confidence || 0.85,
        retry_count: response.plan?.retry_attempt || response.retry_count || 0,
      });
    } catch (error) {
      console.error('Query error:', error);
      
      let errorMessage = 'Failed to process query. Please try again.';
      
      // Check if it's a timeout error
      if (error.code === 'ECONNABORTED') {
        errorMessage = '⏱️ The server took too long to respond. Your query might be too complex or the system is processing heavy workloads. Please try a more specific question or try again later.';
      } else if (error.response?.status === 500) {
        // Server error with potential detail
        const detail = error.response?.data?.detail || '';
        if (detail.toLowerCase().includes('azure') || detail.toLowerCase().includes('openai')) {
          errorMessage = '🔌 Unable to connect to the AI service. The system is experiencing connectivity issues. Please try again in a moment.';
        } else if (detail.toLowerCase().includes('parse') || detail.toLowerCase().includes('json')) {
          errorMessage = '⚠️ Unable to generate a proper response. The AI returned malformed data. Please rephrase your question or try again.';
        } else if (detail.toLowerCase().includes('timeout')) {
          errorMessage = '⏱️ The analysis is taking longer than expected. Please try a simpler question or break it into smaller parts.';
        } else {
          errorMessage = `❌ Server error: ${detail || 'An unexpected error occurred while processing your request. Please try again.'}`;
        }
      } else if (error.response?.status === 404) {
        errorMessage = '🔍 The requested endpoint was not found. Please ensure the backend server is running correctly.';
      } else if (error.response?.status === 400) {
        const detail = error.response?.data?.detail || '';
        errorMessage = `📝 Invalid request: ${detail || 'Please check your query and try again.'}`;
      } else if (!error.response) {
        // Network error
        errorMessage = '🌐 Unable to reach the server. Please check your connection and ensure the backend is running.';
      } else {
        // Generic error with detail if available
        const detail = error.response?.data?.detail || error.message;
        if (detail && detail !== 'Failed to process query. Please try again.') {
          errorMessage = `⚠️ ${detail}`;
        }
      }
      
      setResult({
        error: true,
        message: errorMessage,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery);
  };

  // Build progressive workflow data based on current agent
  const getLoadingWorkflowData = () => {
    const agents = ['planner', 'retriever', 'analyzer', 'generator', 'critic'];
    const currentIndex = agents.indexOf(currentAgent);
    
    const workflowData = {};
    agents.forEach((agent, index) => {
      if (index < currentIndex) {
        workflowData[agent] = { completed: true };
      } else if (index === currentIndex) {
        workflowData[agent] = { active: true };
      } else {
        workflowData[agent] = { active: false };
      }
    });
    
    return workflowData;
  };

  return (
    <div className="space-y-6 md:space-y-8">
      <div className="glass-card p-6 md:p-10 lg:p-12 animate-scale-in">
        <h2 className="text-2xl md:text-3xl font-bold mb-8 bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent flex items-center">
          <Sparkles size={32} className="mr-3 text-primary-400 animate-pulse-slow" />
          Ask a Financial Question
        </h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="relative">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., What is the company's net profit margin for the latest quarter?"
              className="input-field w-full h-36 md:h-40 resize-none text-base md:text-lg"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="btn-primary w-full flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed text-base md:text-lg py-4"
          >
            {loading ? (
              <>
                <Loader size={24} className="animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Send size={22} />
                <span>Submit Query</span>
              </>
            )}
          </button>
        </form>

        <div className="mt-8">
          <p className="text-sm md:text-base text-gray-400 mb-4">💡 Try these examples:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
            {exampleQueries.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(example)}
                disabled={loading}
                className="text-left p-4 md:p-5 rounded-xl bg-black/40 hover:bg-black/60 border border-white/5 hover:border-primary-500/50 transition-all duration-300 text-sm md:text-base text-gray-300 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 animate-fade-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading && currentAgent && (
        <div className="animate-fade-in-up">
          <AgentWorkflow workflowData={getLoadingWorkflowData()} />
        </div>
      )}

      {result && !loading && workflowData && (
        <div className="animate-fade-in-up">
          <AgentWorkflow workflowData={workflowData} />
        </div>
      )}

      {result && !loading && (
        <div className="animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          <ResultDisplay result={result} />
        </div>
      )}
    </div>
  );
};

export default QueryPanel;
