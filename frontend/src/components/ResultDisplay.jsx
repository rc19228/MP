import React from 'react';
import { FileText, AlertCircle, CheckCircle2, BookOpen } from 'lucide-react';

const ResultDisplay = ({ result }) => {
  const renderValue = (value, depth = 0) => {
    if (value === null || value === undefined) {
      return <span className="text-gray-500">Not available</span>;
    }

    if (Array.isArray(value)) {
      if (value.length === 0) return <span className="text-gray-500">[]</span>;
      return (
        <div className="space-y-2">
          {value.map((item, index) => (
            <div key={`${depth}-${index}`} className="pl-3 border-l border-white/10">
              {renderValue(item, depth + 1)}
            </div>
          ))}
        </div>
      );
    }

    if (typeof value === 'object') {
      const entries = Object.entries(value);
      if (entries.length === 0) return <span className="text-gray-500">{'{}'}</span>;
      return (
        <div className="space-y-2">
          {entries.map(([key, val]) => (
            <div key={`${depth}-${key}`} className="bg-black/20 border border-white/5 rounded-lg p-3">
              <div className="text-xs uppercase tracking-wide text-primary-300 mb-1">{key.replace(/_/g, ' ')}</div>
              <div className="text-sm md:text-base text-gray-200">{renderValue(val, depth + 1)}</div>
            </div>
          ))}
        </div>
      );
    }

    if (typeof value === 'boolean') return <span>{value ? 'true' : 'false'}</span>;
    return <span className="whitespace-pre-wrap break-words">{String(value)}</span>;
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
            <div className="text-xs uppercase tracking-wide text-gray-400 mb-2">Planner Output</div>
            {renderValue(result.plan)}
          </div>
        )}

        {result.executive_summary && (
          <div className="mb-6 bg-black/20 p-4 rounded-xl border border-white/5">
            <div className="text-xs uppercase tracking-wide text-gray-400 mb-2">Executive Summary</div>
            <div className="text-gray-200 text-base md:text-lg leading-relaxed whitespace-pre-wrap">{result.executive_summary}</div>
          </div>
        )}

        <div className="mb-6 bg-black/20 p-4 rounded-xl border border-white/5">
          <div className="text-xs uppercase tracking-wide text-gray-400 mb-2">Analysis</div>
          <div className="text-gray-200 text-base md:text-lg">{renderValue(result.analysis || result.answer || result.response || 'No analysis available')}</div>
        </div>

        <div className="mb-6 bg-black/20 p-4 rounded-xl border border-white/5">
          <div className="text-xs uppercase tracking-wide text-gray-400 mb-2">Risk Factors</div>
          <div className="text-gray-200 text-base md:text-lg">{renderValue(result.risk_factors || 'Information not available')}</div>
        </div>

        {result.computed_metrics && (
          <div className="mb-6 bg-black/20 p-4 rounded-xl border border-white/5">
            <div className="text-xs uppercase tracking-wide text-gray-400 mb-2">Computed Metrics</div>
            {renderValue(result.computed_metrics)}
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
