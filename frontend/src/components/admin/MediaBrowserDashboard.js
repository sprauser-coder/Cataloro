import React, { useState, useEffect } from 'react';
import { 
  Image as ImageIcon, 
  Upload, 
  Trash2, 
  Download, 
  Eye, 
  Search, 
  Filter, 
  Grid3X3, 
  List, 
  Folder, 
  File, 
  Calendar, 
  FileImage, 
  X,
  Copy,
  CheckCircle,
  RefreshCw,
  Plus,
  Settings,
  Info,
  Check,
  Square,
  CheckSquare
} from 'lucide-react';

const MediaBrowserDashboard = ({ className = '' }) => {
  const [mediaFiles, setMediaFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [previewImage, setPreviewImage] = useState(null);
  const [copiedUrl, setCopiedUrl] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragOver, setDragOver] = useState(false);

  useEffect(() => {
    fetchMediaFiles();
  }, []);

  const fetchMediaFiles = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      // Fetch admin-uploaded media files
      const response = await fetch(`${backendUrl}/api/admin/media/files`);
      const data = await response.json();
      
      if (data.success) {
        setMediaFiles(data.files || []);
        console.log(`📁 Loaded ${data.files?.length || 0} real media files from uploads directory`);
      } else {
        console.error('Failed to fetch media files:', data);
        setMediaFiles([]);
      }
    } catch (error) {
      console.error('Failed to fetch media files:', error);
      setMediaFiles([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;
    
    try {
      setUploadProgress(10);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      const uploadedFiles = [];
      const totalFiles = files.length;
      
      // Upload files one by one (can be optimized to parallel later)
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const formData = new FormData();
        
        formData.append('file', file);
        formData.append('category', 'uploads');
        formData.append('description', `Uploaded via media browser: ${file.name}`);
        
        // Update progress
        const progressValue = 20 + ((i / totalFiles) * 60);
        setUploadProgress(progressValue);
        
        const response = await fetch(`${backendUrl}/api/admin/media/upload`, {
          method: 'POST',
          body: formData
        });
        
        if (response.ok) {
          const result = await response.json();
          if (result.success && result.file) {
            uploadedFiles.push(result.file);
            console.log(`✅ Uploaded: ${result.file.filename}`);
          }
        } else {
          console.error(`Failed to upload: ${file.name}`, response.status);
        }
      }
      
      setUploadProgress(90);
      
      if (uploadedFiles.length > 0) {
        // Refresh the entire file list to show new uploads with proper metadata
        await fetchMediaFiles();
        
        setUploadModalOpen(false);
        setUploadProgress(100);
        
        console.log(`✅ Successfully uploaded ${uploadedFiles.length} of ${totalFiles} files`);
        
        // Show success message
        alert(`Successfully uploaded ${uploadedFiles.length} file(s)!`);
      } else {
        alert('Failed to upload files. Please try again.');
      }
      
      setTimeout(() => setUploadProgress(0), 2000);
      
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed: ' + error.message);
      setUploadProgress(0);
      setUploadModalOpen(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files);
    }
  };

  // Bulk selection functions
  const toggleFileSelection = (fileId) => {
    setSelectedFiles(prev => 
      prev.includes(fileId) 
        ? prev.filter(id => id !== fileId)
        : [...prev, fileId]
    );
  };

  const selectAllFiles = () => {
    if (selectedFiles.length === filteredFiles.length) {
      setSelectedFiles([]);
    } else {
      setSelectedFiles(filteredFiles.map(file => file.id));
    }
  };

  // Bulk operations
  const bulkDeleteFiles = async () => {
    if (selectedFiles.length === 0) return;
    
    if (!window.confirm(`Are you sure you want to delete ${selectedFiles.length} selected file(s)? This action cannot be undone.`)) {
      return;
    }

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      let deleteCount = 0;

      for (const fileId of selectedFiles) {
        const response = await fetch(`${backendUrl}/api/admin/media/files/${fileId}`, {
          method: 'DELETE'
        });

        if (response.ok) {
          deleteCount++;
        }
      }

      // Remove deleted files from state
      setMediaFiles(prev => prev.filter(file => !selectedFiles.includes(file.id)));
      setSelectedFiles([]);
      
      console.log(`✅ Bulk deleted ${deleteCount} files`);
      alert(`Successfully deleted ${deleteCount} file(s)!`);
      
      // Refresh to ensure sync
      setTimeout(() => fetchMediaFiles(), 500);
      
    } catch (error) {
      console.error('Bulk delete failed:', error);
      alert('Failed to delete files: ' + error.message);
    }
  };

  const bulkDownloadFiles = () => {
    if (selectedFiles.length === 0) return;
    
    selectedFiles.forEach(fileId => {
      const file = mediaFiles.find(f => f.id === fileId);
      if (file) {
        const link = document.createElement('a');
        link.href = file.url;
        link.download = file.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    });
    
    alert(`Started download of ${selectedFiles.length} file(s)!`);
  };

  const deleteFile = async (fileId) => {
    if (!window.confirm('Are you sure you want to delete this file? This action cannot be undone.')) {
      return;
    }
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      // Use the correct API endpoint for deleting files
      const response = await fetch(`${backendUrl}/api/admin/media/files/${fileId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          // Remove from local state
          setMediaFiles(prev => prev.filter(file => file.id !== fileId));
          console.log('✅ File deleted successfully');
          
          // Optionally refresh the entire list to ensure sync
          setTimeout(() => fetchMediaFiles(), 500);
        } else {
          console.error('Delete failed:', result.message);
          alert('Failed to delete file: ' + (result.message || 'Unknown error'));
        }
      } else {
        console.error('Delete request failed:', response.status);
        alert('Failed to delete file. Please try again.');
      }
    } catch (error) {
      console.error('Failed to delete file:', error);
      alert('Failed to delete file: ' + error.message);
    }
  };

  const copyImageUrl = (url) => {
    const fullUrl = `${process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}${url}`;
    navigator.clipboard.writeText(fullUrl);
    setCopiedUrl(url);
    setTimeout(() => setCopiedUrl(''), 2000);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type) => {
    if (type.startsWith('image/')) {
      return <FileImage className="w-5 h-5 text-blue-500" />;
    }
    return <File className="w-5 h-5 text-gray-500" />;
  };

  const filteredFiles = mediaFiles.filter(file => {
    const matchesSearch = file.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         file.description?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterType === 'all' || 
                         (filterType === 'images' && file.type.startsWith('image/')) ||
                         file.category === filterType;
    
    return matchesSearch && matchesFilter;
  });

  const categories = [...new Set(mediaFiles.map(file => file.category))];

  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading media files...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg">
            <ImageIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Media Browser
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Manage admin-uploaded images and media files
            </p>
          </div>
        </div>
        
        <button
          onClick={() => setUploadModalOpen(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Upload Files</span>
        </button>
      </div>

      {/* Controls */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow border border-gray-200 dark:border-gray-600">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div className="flex items-center space-x-4">
            {/* Search */}
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search files..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white w-64"
              />
            </div>

            {/* Filter */}
            <div className="relative">
              <Filter className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="pl-10 pr-8 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white appearance-none"
              >
                <option value="all">All Files</option>
                <option value="images">Images Only</option>
                {categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {filteredFiles.length} of {mediaFiles.length} files
            </span>
            
            {/* View Mode Toggle */}
            <div className="flex items-center space-x-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded ${
                  viewMode === 'grid' 
                    ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow'
                    : 'text-gray-600 dark:text-gray-400'
                }`}
              >
                <Grid3X3 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded ${
                  viewMode === 'list' 
                    ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow'
                    : 'text-gray-600 dark:text-gray-400'
                }`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>

            {/* Bulk Operations */}
            {selectedFiles.length > 0 && (
              <div className="flex items-center space-x-2 px-3 py-1 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                  {selectedFiles.length} selected
                </span>
                <button
                  onClick={bulkDownloadFiles}
                  className="p-1 text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded transition-colors"
                  title="Download selected files"
                >
                  <Download className="w-4 h-4" />
                </button>
                <button
                  onClick={bulkDeleteFiles}
                  className="p-1 text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 hover:bg-red-100 dark:hover:bg-red-900/30 rounded transition-colors"
                  title="Delete selected files"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setSelectedFiles([])}
                  className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                  title="Clear selection"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}

            <button
              onClick={fetchMediaFiles}
              className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Media Grid/List */}
      {filteredFiles.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-12 shadow border border-gray-200 dark:border-gray-600 text-center">
          <ImageIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No Media Files</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {searchTerm || filterType !== 'all' 
              ? 'No files match your search criteria' 
              : 'Upload your first admin media files to get started'
            }
          </p>
          <button
            onClick={() => setUploadModalOpen(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Upload Files
          </button>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
              {filteredFiles.map((file) => (
                <div key={file.id} className="group relative bg-gray-50 dark:bg-gray-700 rounded-lg overflow-hidden">
                  <div className="aspect-square">
                    {file.type.startsWith('image/') ? (
                      <img
                        src={file.url}
                        alt={file.filename}
                        className="w-full h-full object-cover cursor-pointer"
                        onClick={() => setPreviewImage(file)}
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    
                    {/* Fallback for non-images or broken images */}
                    <div className="w-full h-full flex items-center justify-center bg-gray-100 dark:bg-gray-600" style={{ display: file.type.startsWith('image/') ? 'none' : 'flex' }}>
                      {getFileIcon(file.type)}
                    </div>
                  </div>
                  
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all duration-200 flex items-center justify-center opacity-0 group-hover:opacity-100">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setPreviewImage(file)}
                        className="p-2 bg-white bg-opacity-90 text-gray-900 rounded-full hover:bg-opacity-100 transition-all"
                        title="Preview"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => copyImageUrl(file.url)}
                        className="p-2 bg-white bg-opacity-90 text-gray-900 rounded-full hover:bg-opacity-100 transition-all"
                        title="Copy URL"
                      >
                        {copiedUrl === file.url ? <CheckCircle className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
                      </button>
                      <button
                        onClick={() => deleteFile(file.id)}
                        className="p-2 bg-white bg-opacity-90 text-gray-900 rounded-full hover:bg-opacity-100 transition-all"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  
                  <div className="p-3">
                    <div className="text-sm font-medium text-gray-900 dark:text-white truncate" title={file.filename}>
                      {file.filename}
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      {formatFileSize(file.size)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {filteredFiles.map((file) => (
                <div key={file.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-gray-200 dark:bg-gray-600 rounded-lg flex items-center justify-center overflow-hidden">
                      {file.type.startsWith('image/') ? (
                        <img
                          src={file.url}
                          alt={file.filename}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                      ) : null}
                      <div className="w-full h-full flex items-center justify-center" style={{ display: file.type.startsWith('image/') ? 'none' : 'flex' }}>
                        {getFileIcon(file.type)}
                      </div>
                    </div>
                    
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">{file.filename}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        {formatFileSize(file.size)} • {file.category} • Uploaded by {file.uploadedBy}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-500">
                        {new Date(file.uploadedAt).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setPreviewImage(file)}
                      className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                      title="Preview"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => copyImageUrl(file.url)}
                      className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                      title="Copy URL"
                    >
                      {copiedUrl === file.url ? <CheckCircle className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
                    </button>
                    <button
                      onClick={() => deleteFile(file.id)}
                      className="p-2 text-gray-500 hover:text-red-700 dark:text-gray-400 dark:hover:text-red-300 hover:bg-red-100 dark:hover:bg-red-900/30 rounded"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Upload Modal */}
      {uploadModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Upload Media Files</h3>
              <button
                onClick={() => setUploadModalOpen(false)}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragOver
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-300 dark:border-gray-600'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Drag and drop files here, or click to select
              </p>
              
              <input
                type="file"
                multiple
                accept="image/*"
                onChange={(e) => handleFileUpload(e.target.files)}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer inline-block transition-colors"
              >
                Select Files
              </label>
            </div>

            {uploadProgress > 0 && (
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Uploading...</span>
                  <span className="text-sm text-gray-600 dark:text-gray-400">{uploadProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              </div>
            )}

            <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="flex items-start space-x-3">
                <Info className="w-5 h-5 text-blue-500 mt-0.5" />
                <div className="text-sm text-blue-700 dark:text-blue-300">
                  <p className="font-medium mb-1">Admin Media Guidelines:</p>
                  <ul className="space-y-1 text-xs">
                    <li>• Images are for admin/site use only (logos, backgrounds, etc.)</li>
                    <li>• Supported formats: JPG, PNG, SVG, WebP</li>
                    <li>• Max file size: 5MB per image</li>
                    <li>• Files will be accessible via direct URL</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {previewImage && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden max-w-4xl max-h-[90vh] w-full mx-4">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-600">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{previewImage.filename}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {formatFileSize(previewImage.size)} • {previewImage.type}
                </p>
              </div>
              <button
                onClick={() => setPreviewImage(null)}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-4 max-h-[70vh] overflow-auto">
              {previewImage.type.startsWith('image/') ? (
                <img
                  src={previewImage.url}
                  alt={previewImage.filename}
                  className="max-w-full h-auto mx-auto"
                />
              ) : (
                <div className="flex items-center justify-center py-12">
                  {getFileIcon(previewImage.type)}
                  <span className="ml-2 text-gray-600 dark:text-gray-400">Preview not available for this file type</span>
                </div>
              )}
            </div>
            
            <div className="p-4 border-t border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  <p>Category: {previewImage.category}</p>
                  <p>Uploaded by: {previewImage.uploadedBy} on {new Date(previewImage.uploadedAt).toLocaleDateString()}</p>
                  {previewImage.description && <p>Description: {previewImage.description}</p>}
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => copyImageUrl(previewImage.url)}
                    className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                  >
                    {copiedUrl === previewImage.url ? 'Copied!' : 'Copy URL'}
                  </button>
                  <a
                    href={previewImage.url}
                    download={previewImage.filename}
                    className="px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm"
                  >
                    Download
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="text-center text-sm text-gray-500 dark:text-gray-400">
        Media Browser | 
        Admin-uploaded files only • Direct URL access • File management | 
        Total files: {mediaFiles.length}
      </div>
    </div>
  );
};

export default MediaBrowserDashboard;