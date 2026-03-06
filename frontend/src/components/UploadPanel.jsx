import React, { useRef, useState } from 'react';
import { Upload, File, CheckCircle, XCircle, Loader, ArrowRight, Sparkles } from 'lucide-react';
import { uploadPDF } from '../api/api';

const UploadPanel = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const isPdfFile = (candidate) => {
    if (!candidate) return false;
    return candidate.type === 'application/pdf' || candidate.name?.toLowerCase().endsWith('.pdf');
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (isPdfFile(droppedFile)) {
        setFile(droppedFile);
        setUploadStatus(null);
      } else {
        setUploadStatus({ type: 'error', message: 'Please upload a PDF file' });
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (isPdfFile(selectedFile)) {
        setFile(selectedFile);
        setUploadStatus(null);
      } else {
        setUploadStatus({ type: 'error', message: 'Please upload a PDF file' });
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setUploadStatus(null);
    setUploadResult(null);

    try {
      const result = await uploadPDF(file);
      setUploadResult(result);
      setUploadStatus({
        type: 'success',
        message: `✅ Successfully processed ${file.name}!`,
      });
      setFile(null);
      if (onUploadSuccess) onUploadSuccess(result);
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: error.response?.data?.detail || 'Upload failed. Please try again.',
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="glass-card p-6 md:p-10 lg:p-12 animate-scale-in">
      <h2 className="text-2xl md:text-3xl font-bold mb-8 bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">
        Upload Financial Documents
      </h2>

      <div
        className={`relative border-2 border-dashed rounded-2xl p-8 md:p-12 lg:p-16 text-center transition-all duration-500 mb-6 ${
          dragActive
            ? 'border-primary-500 bg-primary-500/20 scale-105 shadow-lg shadow-primary-500/50'
            : 'border-white/10 hover:border-primary-500/50 hover:bg-black/30'
        }`}
        role="button"
        tabIndex={0}
        onClick={() => {
          if (!uploading) {
            fileInputRef.current?.click();
          }
        }}
        onKeyDown={(e) => {
          if ((e.key === 'Enter' || e.key === ' ') && !uploading) {
            e.preventDefault();
            fileInputRef.current?.click();
          }
        }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          className="hidden"
          disabled={uploading}
        />

        <div className={`transition-all duration-300 ${dragActive ? 'scale-110' : ''}`}>
          <Upload size={56} className={`mx-auto mb-6 transition-all duration-300 ${dragActive ? 'text-primary-400 animate-bounce-subtle' : 'text-primary-400/70'}`} />
          <h3 className="text-xl md:text-2xl font-semibold mb-3">
            {file ? file.name : 'Drop your PDF here'}
          </h3>
          <p className="text-gray-400 mb-6 text-sm md:text-base">
            {file
              ? `${(file.size / 1024 / 1024).toFixed(2)} MB`
              : 'or click to browse files'}
          </p>

          {file && !uploading && (
            <button 
              onClick={(e) => {
                e.stopPropagation();
                handleUpload();
              }} 
              className="btn-primary inline-flex items-center space-x-2 text-base md:text-lg animate-fade-in"
            >
              <Upload size={22} />
              <span>Upload Document</span>
            </button>
          )}

          {uploading && (
            <div className="flex items-center justify-center space-x-3 text-primary-400 animate-fade-in">
              <Loader size={24} className="animate-spin" />
              <span className="text-base md:text-lg">Processing document...</span>
            </div>
          )}
        </div>
      </div>

      {uploadStatus && uploadStatus.type === 'success' && uploadResult && (
        <div className="mb-6 animate-fade-in-up">
          <div className="bg-gradient-to-br from-success-500/20 to-success-600/20 border-2 border-success-500/40 rounded-2xl p-6 md:p-8 shadow-lg shadow-success-500/20">
            <div className="flex items-start space-x-4 mb-6">
              <div className="flex-shrink-0 w-14 h-14 rounded-2xl bg-success-500/30 flex items-center justify-center">
                <CheckCircle size={28} className="text-success-400" />
              </div>
              <div className="flex-1">
                <h3 className="text-xl md:text-2xl font-bold text-success-100 mb-2">
                  Document Processed Successfully! 🎉
                </h3>
                <p className="text-success-200/80 text-sm md:text-base">
                  Your document has been analyzed and indexed for intelligent querying
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-black/30 rounded-xl p-4 border border-success-500/20">
                <div className="text-success-400 text-sm font-medium mb-1">Document</div>
                <div className="text-white text-lg font-bold truncate">{uploadResult.filename}</div>
              </div>
              <div className="bg-black/30 rounded-xl p-4 border border-success-500/20">
                <div className="text-success-400 text-sm font-medium mb-1">Chunks Created</div>
                <div className="text-white text-2xl font-bold">{uploadResult.chunks_created}</div>
              </div>
              <div className="bg-black/30 rounded-xl p-4 border border-success-500/20">
                <div className="text-success-400 text-sm font-medium mb-1">Status</div>
                <div className="text-white text-lg font-bold capitalize">{uploadResult.status}</div>
              </div>
            </div>

            <div className="bg-primary-500/10 border border-primary-500/30 rounded-xl p-4 mb-4">
              <div className="flex items-start space-x-3">
                <Sparkles size={20} className="text-primary-400 flex-shrink-0 mt-0.5" />
                <p className="text-sm md:text-base text-gray-300">
                  <strong className="text-white">Ready to analyze:</strong> Your document has been split into {uploadResult.chunks_created} semantic chunks and vectorized for intelligent retrieval. You can now ask questions about financial metrics, trends, risks, and more!
                </p>
              </div>
            </div>

            <div className="bg-black/30 border border-white/10 rounded-xl p-4 mb-4">
              <p className="text-sm text-gray-300 mb-2">Try one of these prompts next:</p>
              <ul className="text-sm text-gray-400 space-y-1">
                <li>• What is the net profit margin and how did it change year-over-year?</li>
                <li>• Summarize key revenue drivers and major cost pressures.</li>
                <li>• What are the top financial risks called out in this report?</li>
              </ul>
            </div>

            <button
              onClick={() => window.dispatchEvent(new CustomEvent('switchTab', { detail: 'query' }))}
              className="btn-primary w-full flex items-center justify-center space-x-2 text-base md:text-lg"
            >
              <span>Start Asking Questions</span>
              <ArrowRight size={22} />
            </button>
          </div>
        </div>
      )}

      {uploadStatus && uploadStatus.type === 'error' && (
        <div
          className="p-5 md:p-6 rounded-xl flex items-start space-x-4 animate-slide-up mb-6 bg-error-500/20 border border-error-500/40"
        >
          <XCircle size={26} className="text-error-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="text-lg font-bold text-error-200 mb-1">Upload Failed</h4>
            <p className="text-base md:text-lg text-error-200">{uploadStatus.message}</p>
          </div>
        </div>
      )}

      <div className="p-6 md:p-8 bg-black/40 rounded-2xl border border-white/5">
        <h4 className="font-semibold mb-4 flex items-center text-base md:text-lg">
          <File size={22} className="mr-3 text-primary-400" />
          Supported Documents
        </h4>
        <ul className="space-y-3 text-sm md:text-base text-gray-400">
          <li className="flex items-start">
            <span className="text-primary-400 mr-3">•</span>
            <span>Annual Reports & Financial Statements</span>
          </li>
          <li className="flex items-start">
            <span className="text-primary-400 mr-3">•</span>
            <span>Balance Sheets & Income Statements</span>
          </li>
          <li className="flex items-start">
            <span className="text-primary-400 mr-3">•</span>
            <span>Cash Flow Reports & Earnings Reports</span>
          </li>
          <li className="flex items-start">
            <span className="text-primary-400 mr-3">•</span>
            <span>Investment Prospectuses</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default UploadPanel;
