import React from 'react';
import { FileText, Database, Clock, CheckCircle } from 'lucide-react';

const MetricsCards = ({ stats, loading = false }) => {
  const metrics = [
    {
      label: 'Documents',
      value: stats?.total_documents || 0,
      icon: FileText,
      color: 'text-primary-400',
      bgColor: 'bg-primary-500/20',
      borderColor: 'border-primary-500/30',
    },
    {
      label: 'Total Chunks',
      value: stats?.total_chunks || 0,
      icon: Database,
      color: 'text-accent-400',
      bgColor: 'bg-accent-500/20',
      borderColor: 'border-accent-500/30',
    },
    {
      label: 'Queries Processed',
      value: stats?.queries_processed || 0,
      icon: CheckCircle,
      color: 'text-success-400',
      bgColor: 'bg-success-500/20',
      borderColor: 'border-success-500/30',
    },
    {
      label: 'Avg Response Time',
      value: stats?.avg_response_time ? `${stats.avg_response_time.toFixed(2)}s` : '0s',
      icon: Clock,
      color: 'text-warning-400',
      bgColor: 'bg-warning-500/20',
      borderColor: 'border-warning-500/30',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-8">
      {metrics.map((metric, index) => (
        <div 
          key={index} 
          className={`metric-card border ${metric.borderColor} hover:border-${metric.color.split('-')[1]}-500/50 ${loading ? 'opacity-50 animate-pulse' : ''}`}
          style={{ animationDelay: `${index * 0.1}s` }}
        >
          <div className={`inline-flex p-4 rounded-xl ${metric.bgColor} mb-4 transition-transform duration-300 hover:scale-110 relative`}>
            <metric.icon size={28} className={metric.color} />
            {loading && (
              <div className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-primary-400 animate-bounce"></div>
            )}
          </div>
          <div className="text-3xl md:text-4xl font-bold mb-2">{metric.value}</div>
          <div className="text-sm md:text-base text-gray-400">{metric.label}</div>
        </div>
      ))}
    </div>
  );
};

export default MetricsCards;
