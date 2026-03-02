import React, { useState } from 'react';
import { Send, Sparkles, Loader } from 'lucide-react';
import { askQuery } from '../api/api';
import ResultDisplay from './ResultDisplay';
import AgentWorkflow from './AgentWorkflow';

const QueryPanel = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [workflowData, setWorkflowData] = useState(null);

  const exampleQueries = [
    "What is the company's revenue growth over the past 3 years?",
    "Analyze the company's debt-to-equity ratio",
    "What are the key risk factors mentioned?",
    "Summarize the cash flow trends",
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    setResult(null);
    setWorkflowData(null);

    try {
      const response = await askQuery(query);
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
        retry_count: response.retry_count || 0,
      });
    } catch (error) {
      setResult({
        error: true,
        message: error.response?.data?.detail || 'Failed to process query. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery);
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

      {loading && (
        <div className="animate-fade-in-up">
          <AgentWorkflow 
            workflowData={{
              planner: { active: true },
              retriever: { active: false },
              analyzer: { active: false },
              generator: { active: false },
              critic: { active: false },
            }}
          />
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
