import React from 'react';
import { FileText, AlertCircle, CheckCircle2, BookOpen } from 'lucide-react';

const ResultDisplay = ({ result }) => {
  // Render plan in a compact, readable format
  const renderPlan = (plan) => {
    if (!plan || typeof plan !== 'object') return null;
    
    return (
      <div className="space-y-3">
        {plan.intent && (
          <div className="flex items-start gap-3">
            <span className="text-primary-400 font-semibold min-w-[120px]">Intent:</span>
            <span className="text-gray-200">{plan.intent.replace(/_/g, ' ')}</span>
          </div>
        )}
        {plan.metrics_required && plan.metrics_required.length > 0 && (
          <div className="flex items-start gap-3">
            <span className="text-primary-400 font-semibold min-w-[120px]">Metrics:</span>
            <span className="text-gray-200">{Array.isArray(plan.metrics_required) ? plan.metrics_required.join(', ') : plan.metrics_required}</span>
          </div>
        )}
        {plan.time_range && (
          <div className="flex items-start gap-3">
            <span className="text-primary-400 font-semibold min-w-[120px]">Time Range:</span>
            <span className="text-gray-200">{plan.time_range}</span>
          </div>
        )}
      </div>
    );
  };

  // Render computed metrics as a clean table
  const renderMetrics = (metrics) => {
    if (!metrics || typeof metrics !== 'object') return null;
    const entries = Object.entries(metrics);
    if (entries.length === 0) return <span className="text-gray-500">No metrics available</span>;

    return (
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left py-2 px-3 text-primary-400 font-semibold">Metric</th>
              <th className="text-right py-2 px-3 text-primary-400 font-semibold">Value</th>
            </tr>
          </thead>
          <tbody>
            {entries.map(([key, value]) => (
              <tr key={key} className="border-b border-white/5 hover:bg-white/5">
                <td className="py-3 px-3 text-gray-300">{key.replace(/_/g, ' ')}</td>
                <td className="py-3 px-3 text-right text-gray-200 font-medium">
                  {typeof value === 'object' ? JSON.stringify(value) : value}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  // Render risk factors as bullet list or text
  const renderRiskFactors = (risks) => {
    if (!risks) return <span className="text-gray-500">No risk factors identified</span>;
    
    if (Array.isArray(risks)) {
      return (
        <ul className="space-y-3">
          {risks.map((risk, idx) => (
            <li key={idx} className="text-gray-200 leading-relaxed flex gap-3">
              <span className="text-warning-400 font-semibold flex-shrink-0">{idx + 1})</span>
              <span>{risk}</span>
            </li>
          ))}
        </ul>
      );
    }
    
    if (typeof risks === 'string') {
      // Check if it's a numbered list (e.g., "1) ", "2) ")
      const lines = risks.split('\n').filter(line => line.trim());
      const isNumberedList = lines.some(line => /^\d+\)/.test(line.trim()));
      
      if (lines.length > 1) {
        return (
          <ul className="space-y-3">
            {lines.map((line, idx) => {
              // Remove the number prefix if it exists for cleaner display
              const cleanLine = line.replace(/^\d+\)\s*/, '').trim();
              return (
                <li key={idx} className="text-gray-200 leading-relaxed flex gap-3">
                  <span className="text-warning-400 font-semibold flex-shrink-0">{idx + 1})</span>
                  <span>{cleanLine}</span>
                </li>
              );
            })}
          </ul>
        );
      }
      return <p className="text-gray-200 leading-relaxed">{risks}</p>;
    }
    
    return <pre className="text-gray-200 whitespace-pre-wrap">{JSON.stringify(risks, null, 2)}</pre>;
  };

  // Render analysis (can be string or object)
  const renderAnalysis = (analysis) => {
    if (!analysis) return <span className="text-gray-500">No analysis available</span>;
    
    if (typeof analysis === 'string') {
      // Split by double line breaks for paragraph formatting
      const paragraphs = analysis.split('\n\n').filter(p => p.trim());
      
      if (paragraphs.length > 1) {
        return (
          <div className="space-y-5">
            {paragraphs.map((para, idx) => {
              const trimmedPara = para.trim();
              
              // Check if paragraph starts with a section label (e.g., "Company Name:", "Interpretation:")
              const sectionMatch = trimmedPara.match(/^([A-Za-z\s&]+):\s*(.+)/s);
              
              if (sectionMatch) {
                return (
                  <div key={idx} className="border-l-2 border-primary-500/40 pl-4">
                    <div className="text-sm font-semibold text-primary-400 mb-2">{sectionMatch[1]}</div>
                    <p className="text-gray-200 leading-relaxed">{sectionMatch[2]}</p>
                  </div>
                );
              }
              
              return (
                <p key={idx} className="text-gray-200 leading-relaxed">
                  {trimmedPara}
                </p>
              );
            })}
          </div>
        );
      }
      
      return <p className="text-gray-200 whitespace-pre-wrap leading-relaxed">{analysis}</p>;
    }
    
    if (typeof analysis === 'object') {
      return (
        <div className="space-y-4">
          {Object.entries(analysis).map(([key, value]) => (
            <div key={key} className="border-l-2 border-primary-500/30 pl-4">
              <div className="text-sm font-semibold text-primary-400 mb-2">{key.replace(/_/g, ' ').toUpperCase()}</div>
              <div className="text-gray-200">
                {typeof value === 'object' ? (
                  <pre className="text-sm bg-black/40 p-3 rounded overflow-x-auto">{JSON.stringify(value, null, 2)}</pre>
                ) : (
                  <span>{String(value)}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      );
    }
    
    return <span className="text-gray-200">{String(analysis)}</span>;
  };

  // Generic renderValue for additional fields
  const renderValue = (value) => {
    if (value === null || value === undefined) {
      return <span className="text-gray-500">Not available</span>;
    }
    if (typeof value === 'object') {
      return <pre className="text-sm bg-black/40 p-3 rounded overflow-x-auto">{JSON.stringify(value, null, 2)}</pre>;
    }
    return <span className="text-gray-200 whitespace-pre-wrap">{String(value)}</span>;
  };

  const primaryKeys = new Set([
    'query',
    'plan',
    'executive_summary',
    'analysis',
    'risk_factors',
    'computed_metrics',
    'confidence',
    'retry_count',
    'final_weight',
    'status',
    'sources',
    'error',
    'message',
  ]);

  const additionalFields = Object.entries(result || {}).filter(([key]) => !primaryKeys.has(key));

  if (result?.error) {
    return (
      <div className="glass-card p-6 md:p-10 animate-fade-in-up">
        <div className="flex items-start space-x-5">
          <div className="flex-shrink-0 w-14 h-14 rounded-2xl bg-error-500/20 flex items-center justify-center border border-error-500/30">
            <AlertCircle size={28} className="text-error-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-2xl font-bold text-error-400 mb-3">Error</h3>
            <p className="text-gray-300 text-base md:text-lg">{result.message}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card p-6 md:p-10 lg:p-12 animate-fade-in-up">
      <div className="flex items-start space-x-5 mb-8">
        <div className="flex-shrink-0 w-14 h-14 md:w-16 md:h-16 rounded-2xl bg-gradient-to-br from-primary-600 to-primary-500 flex items-center justify-center shadow-lg shadow-primary-500/50">
          <CheckCircle2 size={32} className="text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-2xl md:text-3xl font-bold mb-3 bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">
            Analysis Result
          </h3>
          {result.confidence !== undefined && (
            <div className="flex items-center space-x-3">
              <span className="text-sm md:text-base text-gray-400">Confidence:</span>
              <span
                className={`text-base md:text-lg font-bold ${
                  result.confidence >= 0.7
                    ? 'text-success-400'
                    : result.confidence >= 0.5
                    ? 'text-warning-400'
                    : 'text-error-400'
                }`}
              >
                {(result.confidence * 100).toFixed(1)}%
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="prose prose-invert max-w-none">
        {result.query && (
          <div className="mb-6 bg-black/20 p-4 rounded-xl border border-white/5">
            <div className="text-xs uppercase tracking-wide text-gray-400 mb-1">Query</div>
            <div className="text-gray-100 text-base md:text-lg">{result.query}</div>
          </div>
        )}

        {result.plan && (
          <div className="mb-6 bg-black/20 p-4 rounded-xl border border-white/5">
            <div className="flex items-center justify-between mb-2">
              <div className="text-xs uppercase tracking-wide text-gray-400">Planner Output</div>
              {result.plan.retry_attempt && (
                <span className="text-xs px-2 py-1 bg-accent-500/20 text-accent-400 rounded-full border border-accent-500/30">
                  Retry #{result.plan.retry_attempt}
                </span>
              )}
            </div>
            {result.plan.status && (
              <div className="mb-3 text-sm text-gray-300 italic">
                {result.plan.status}
              </div>
            )}
            <div className="mt-3">
              {renderPlan(result.plan)}
            </div>
            {result.plan.adjustments && result.plan.adjustments.length > 0 && (
              <div className="mt-4 p-3 bg-primary-500/10 border border-primary-500/20 rounded-lg">
                <div className="text-xs uppercase tracking-wide text-primary-400 mb-2">Parameter Adjustments</div>
                <div className="space-y-2">
                  {result.plan.adjustments.map((adj, idx) => (
                    <div key={idx} className="text-sm text-gray-300">
                      <span className="font-semibold text-primary-300">{adj.parameter}:</span>{' '}
                      <span className="text-gray-400">{adj.original}</span>
                      <span className="text-accent-400 mx-1">→</span>
                      <span className="text-success-400">{adj.adjusted}</span>
                      {adj.reason && (
                        <div className="text-xs text-gray-400 mt-1 ml-4">→ {adj.reason}</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {result.executive_summary && (
          <div className="mb-6 bg-black/20 p-5 rounded-xl border border-white/5">
            <div className="text-xs uppercase tracking-wide text-gray-400 mb-3">Executive Summary</div>
            <div className="text-gray-200 text-base md:text-lg leading-relaxed">{result.executive_summary}</div>
          </div>
        )}

        <div className="mb-6 bg-black/20 p-5 rounded-xl border border-white/5">
          <div className="text-xs uppercase tracking-wide text-gray-400 mb-4">Analysis</div>
          <div className="text-gray-200 text-base md:text-lg">{renderAnalysis(result.analysis || result.answer || result.response)}</div>
        </div>

        <div className="mb-6 bg-black/20 p-5 rounded-xl border border-white/5">
          <div className="text-xs uppercase tracking-wide text-gray-400 mb-4">Risk Factors</div>
          <div className="text-gray-200 text-base md:text-lg">{renderRiskFactors(result.risk_factors)}</div>
        </div>

        {result.computed_metrics && Object.keys(result.computed_metrics).length > 0 && (
          <div className="mb-6 bg-black/20 p-5 rounded-xl border border-white/5">
            <div className="text-xs uppercase tracking-wide text-gray-400 mb-4">Computed Metrics</div>
            {renderMetrics(result.computed_metrics)}
          </div>
        )}

        {additionalFields.length > 0 && (
          <div className="mb-6 bg-black/20 p-4 rounded-xl border border-white/5">
            <div className="text-xs uppercase tracking-wide text-gray-400 mb-2">Additional Output</div>
            <div className="space-y-2">
              {additionalFields.map(([key, value]) => (
                <div key={key} className="bg-black/20 border border-white/5 rounded-lg p-3">
                  <div className="text-xs uppercase tracking-wide text-primary-300 mb-1">{key.replace(/_/g, ' ')}</div>
                  <div className="text-sm md:text-base text-gray-200">{renderValue(value)}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {result.sources && result.sources.length > 0 && (
        <div className="mt-10 pt-8 border-t border-white/10 animate-fade-in" style={{ animationDelay: '0.2s' }}>
          <h4 className="text-lg md:text-xl font-semibold mb-6 flex items-center text-gray-300">
            <BookOpen size={24} className="mr-3 text-primary-400" />
            Source Documents
          </h4>
          <div className="space-y-4">
            {result.sources.map((source, index) => (
              <div
                key={index}
                className="p-5 md:p-6 bg-black/40 rounded-2xl border border-white/5 hover:bg-black/50 hover:border-primary-500/30 transition-all duration-300 hover:scale-[1.02] animate-fade-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="flex items-start space-x-4">
                  <FileText size={24} className="text-accent-400 flex-shrink-0 mt-1" />
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
                      <span className="font-medium text-white text-base md:text-lg">
                        {source.document || `Document ${index + 1}`}
                      </span>
                      {source.similarity !== undefined && (
                        <span className="text-xs px-3 py-1 bg-primary-500/20 text-primary-400 rounded-full border border-primary-500/30">
                          {(source.similarity * 100).toFixed(1)}% match
                        </span>
                      )}
                    </div>
                    <p className="text-sm md:text-base text-gray-400 line-clamp-3 leading-relaxed">
                      {source.content || source.text || 'No preview available'}
                    </p>
                    {source.metadata && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {Object.entries(source.metadata).map(([key, value]) => (
                          <span
                            key={key}
                            className="text-xs px-2 py-1 bg-black/40 text-gray-400 rounded border border-white/5"
                          >
                            {key}: {value}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.retry_count > 0 && (
        <div className="mt-8 p-5 md:p-6 bg-warning-500/10 border border-warning-500/30 rounded-2xl animate-fade-in" style={{ animationDelay: '0.3s' }}>
          <p className="text-sm md:text-base text-warning-400">
            ℹ️ This response was refined through {result.retry_count} iteration
            {result.retry_count > 1 ? 's' : ''} to achieve higher confidence.
          </p>
        </div>
      )}
    </div>
  );
};

export default ResultDisplay;
