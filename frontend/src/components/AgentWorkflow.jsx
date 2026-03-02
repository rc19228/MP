import React from 'react';
import { Lightbulb, Search, BarChart3, FileText, CheckCircle, ArrowRight } from 'lucide-react';

const AgentWorkflow = ({ currentStep, workflowData }) => {
  const agents = [
    { id: 'planner', name: 'Planner', icon: Lightbulb, description: 'Query analysis' },
    { id: 'retriever', name: 'Retriever', icon: Search, description: 'Document search' },
    { id: 'analyzer', name: 'Analyzer', icon: BarChart3, description: 'Context analysis' },
    { id: 'generator', name: 'Generator', icon: FileText, description: 'Response generation' },
    { id: 'critic', name: 'Critic', icon: CheckCircle, description: 'Quality validation' },
  ];

  const getStepStatus = (agentId) => {
    if (!workflowData) return 'pending';
    const stepData = workflowData[agentId];
    if (stepData?.completed) return 'completed';
    if (stepData?.active) return 'active';
    return 'pending';
  };

  return (
    <div className="glass-card p-6 md:p-8 lg:p-10 mb-6 md:mb-8 animate-scale-in">
      <h3 className="text-xl md:text-2xl font-bold mb-8 flex items-center flex-wrap gap-3">
        <span className="bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">
          Agent Pipeline
        </span>
        {workflowData?.retry_count > 0 && (
          <span className="text-xs md:text-sm px-3 py-1 bg-warning-500/20 text-warning-400 rounded-full border border-warning-500/30 animate-fade-in">
            Retry #{workflowData.retry_count}
          </span>
        )}
      </h3>

      <div className="flex flex-col md:flex-row items-center justify-between gap-4 md:gap-2">
        {agents.map((agent, index) => {
          const status = getStepStatus(agent.id);
          const isActive = status === 'active';
          const isCompleted = status === 'completed';

          return (
            <React.Fragment key={agent.id}>
              <div className="flex-1 flex flex-col items-center w-full md:w-auto animate-fade-in" style={{ animationDelay: `${index * 0.1}s` }}>
                <div
                  className={`relative w-20 h-20 md:w-20 md:h-20 lg:w-24 lg:h-24 rounded-2xl flex items-center justify-center transition-all duration-500 ${
                    isActive
                      ? 'bg-gradient-to-br from-primary-600 to-primary-500 shadow-2xl shadow-primary-500/50 scale-110 animate-glow'
                      : isCompleted
                      ? 'bg-gradient-to-br from-success-600 to-success-500 shadow-lg shadow-success-500/30'
                      : 'bg-black/40 border-2 border-white/10'
                  }`}
                >
                  <agent.icon
                    size={isActive || isCompleted ? 36 : 32}
                    className={`transition-all duration-300 ${
                      isActive || isCompleted ? 'text-white' : 'text-gray-500'
                    }`}
                  />
                  {isActive && (
                    <div className="absolute inset-0 rounded-2xl animate-ping bg-primary-500/40" />
                  )}
                </div>
                <div className="mt-4 text-center">
                  <div
                    className={`font-semibold text-sm md:text-base ${
                      isActive || isCompleted ? 'text-white' : 'text-gray-500'
                    }`}
                  >
                    {agent.name}
                  </div>
                  <div className="text-xs md:text-sm text-gray-500 mt-1">
                    {agent.description}
                  </div>
                </div>
              </div>

              {index < agents.length - 1 && (
                <ArrowRight
                  size={28}
                  className={`hidden md:block mx-2 flex-shrink-0 transition-all duration-500 ${
                    isCompleted ? 'text-success-400 scale-110' : 'text-gray-600'
                  }`}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>

      {workflowData?.confidence !== undefined && (
        <div className="mt-8 pt-8 border-t border-white/10 animate-fade-in" style={{ animationDelay: '0.3s' }}>
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm md:text-base text-gray-400">Response Confidence</span>
            <span className="text-base md:text-lg font-bold">{(workflowData.confidence * 100).toFixed(1)}%</span>
          </div>
          <div className="w-full h-3 bg-black/40 rounded-full overflow-hidden border border-white/10">
            <div
              className={`h-full rounded-full transition-all duration-1000 ease-out ${
                workflowData.confidence >= 0.7
                  ? 'bg-gradient-to-r from-success-600 to-success-400 shadow-lg shadow-success-500/50'
                  : workflowData.confidence >= 0.5
                  ? 'bg-gradient-to-r from-warning-600 to-warning-400 shadow-lg shadow-warning-500/50'
                  : 'bg-gradient-to-r from-error-600 to-error-400 shadow-lg shadow-error-500/50'
              }`}
              style={{ width: `${workflowData.confidence * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentWorkflow;
