import React, { useState, useEffect } from 'react';
import { 
  Image as ImageIcon, 
  Upload, 
  Search, 
  Grid3X3, 
  List, 
  X,
  Check,
  RefreshCw,
  Folder,
  ExternalLink
} from 'lucide-react';

const MediaSelector = ({ 
  isOpen, 
  onClose, 
  onSelect, 
  title = "Select Media", 
  allowUpload = true,
  acceptedTypes = "image/*",
  multiple = false 
}) => {
  const [mediaFiles, setMediaFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('grid');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedItems, setSelectedItems] = useState([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchMediaFiles();
    }
  }, [isOpen]);

  const fetchMediaFiles = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      const response = await fetch(`${backendUrl}/api/admin/media/files`);
      const data = await response.json();
      
      if (data.success) {
        setMediaFiles(data.files || []);
        console.log(`📁 MediaSelector loaded ${data.files?.length || 0} real media files`);
      } else {
        console.error('MediaSelector: Failed to fetch media files:', data);
        setMediaFiles([]);
      }
    } catch (error) {
      console.error('MediaSelector: Failed to fetch media files:', error);
      setMediaFiles([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;

    setUploading(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      let uploadCount = 0;
      
      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', 'uploads');
        formData.append('description', `Uploaded via media selector: ${file.name}`);

        const response = await fetch(`${backendUrl}/api/admin/media/upload`, {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            uploadCount++;
            console.log(`✅ MediaSelector uploaded: ${data.file.filename}`);
          }
        } else {
          console.error(`Failed to upload: ${file.name}`, response.status);
        }
      }
      
      // Refresh the media list to show new uploads
      if (uploadCount > 0) {
        await fetchMediaFiles();
        console.log(`✅ MediaSelector: Successfully uploaded ${uploadCount} of ${files.length} files`);
      }
      
    } catch (error) {
      console.error('MediaSelector: Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  const filteredFiles = mediaFiles.filter(file => 
    file.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
    file.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const toggleSelection = (file) => {
    if (multiple) {
      setSelectedItems(prev => 
        prev.find(item => item.id === file.id)
          ? prev.filter(item => item.id !== file.id)
          : [...prev, file]
      );
    } else {
      setSelectedItems([file]);
    }
  };

  const handleSelect = () => {
    if (selectedItems.length > 0) {
      onSelect(multiple ? selectedItems : selectedItems[0]);
      onClose();
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Choose from existing media or upload new files
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Controls */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center space-x-4">
              {/* Search */}
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search media files..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white w-64"
                />
              </div>

              {/* View Mode Toggle */}
              <div className="flex items-center border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 ${viewMode === 'grid' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <Grid3X3 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 ${viewMode === 'list' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <List className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Upload Button */}
            {allowUpload && (
              <label className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors cursor-pointer flex items-center space-x-2">
                <Upload className="w-4 h-4" />
                <span>{uploading ? 'Uploading...' : 'Upload New'}</span>
                <input
                  type="file"
                  accept={acceptedTypes}
                  multiple
                  onChange={(e) => handleFileUpload(Array.from(e.target.files))}
                  className="hidden"
                  disabled={uploading}
                />
              </label>
            )}
          </div>

          <p className="text-sm text-gray-600 dark:text-gray-400">
            {filteredFiles.length} files available • {selectedItems.length} selected
          </p>
        </div>

        {/* Media Grid/List */}
        <div className="p-6 max-h-96 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
              <span className="ml-2 text-gray-600 dark:text-gray-400">Loading media files...</span>
            </div>
          ) : filteredFiles.length === 0 ? (
            <div className="text-center py-12">
              <Folder className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No files found</h4>
              <p className="text-gray-600 dark:text-gray-400">
                {searchTerm ? 'Try a different search term' : 'Upload your first media file'}
              </p>
            </div>
          ) : (
            <div className={viewMode === 'grid' 
              ? 'grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4' 
              : 'space-y-2'
            }>
              {filteredFiles.map((file) => {
                const isSelected = selectedItems.find(item => item.id === file.id);
                
                if (viewMode === 'grid') {
                  return (
                    <div
                      key={file.id}
                      onClick={() => toggleSelection(file)}
                      className={`relative group cursor-pointer rounded-lg border-2 transition-all ${
                        isSelected 
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                      }`}
                    >
                      <div className="aspect-square relative overflow-hidden rounded-t-lg">
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
                        <div className="hidden w-full h-full items-center justify-center bg-gray-100 dark:bg-gray-700">
                          <ImageIcon className="w-8 h-8 text-gray-400" />
                        </div>
                        
                        {isSelected && (
                          <div className="absolute inset-0 bg-blue-600 bg-opacity-20 flex items-center justify-center">
                            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                              <Check className="w-5 h-5 text-white" />
                            </div>
                          </div>
                        )}
                      </div>
                      
                      <div className="p-2">
                        <p className="text-xs font-medium text-gray-900 dark:text-white truncate">
                          {file.filename}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {formatFileSize(file.size)}
                        </p>
                      </div>
                    </div>
                  );
                } else {
                  return (
                    <div
                      key={file.id}
                      onClick={() => toggleSelection(file)}
                      className={`flex items-center space-x-4 p-3 rounded-lg cursor-pointer transition-all ${
                        isSelected 
                          ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800' 
                          : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                    >
                      <div className="w-12 h-12 flex-shrink-0 rounded-lg overflow-hidden">
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
                        <div className="hidden w-full h-full items-center justify-center bg-gray-100 dark:bg-gray-700">
                          <ImageIcon className="w-6 h-6 text-gray-400" />
                        </div>
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {file.filename}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {file.description || 'No description'}
                        </p>
                        <p className="text-xs text-gray-400">
                          {formatFileSize(file.size)} • {new Date(file.uploadedAt).toLocaleDateString()}
                        </p>
                      </div>
                      
                      {isSelected && (
                        <div className="flex-shrink-0">
                          <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                            <Check className="w-4 h-4 text-white" />
                          </div>
                        </div>
                      )}
                    </div>
                  );
                }
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {selectedItems.length > 0 && (
              <span>
                {selectedItems.length} file{selectedItems.length !== 1 ? 's' : ''} selected
              </span>
            )}
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSelect}
              disabled={selectedItems.length === 0}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Select {selectedItems.length > 0 && `(${selectedItems.length})`}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MediaSelector;