/**
 * CATALORO - Mobile Camera Capture Component
 * Camera integration for creating listings with touch-optimized controls
 */

import React, { useState, useRef, useEffect } from 'react';
import { 
  Camera, 
  X, 
  RotateCcw, 
  FlashOff, 
  Flash, 
  Check,
  RefreshCw,
  Image as ImageIcon,
  Upload
} from 'lucide-react';

function MobileCameraCapture({ 
  isOpen, 
  onClose, 
  onCapture, 
  maxPhotos = 5,
  quality = 0.8 
}) {
  const [stream, setStream] = useState(null);
  const [photos, setPhotos] = useState([]);
  const [isCapturing, setIsCapturing] = useState(false);
  const [flashMode, setFlashMode] = useState('off');
  const [facingMode, setFacingMode] = useState('environment'); // 'user' for front, 'environment' for back
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      startCamera();
    } else {
      stopCamera();
    }
    
    return () => stopCamera();
  }, [isOpen, facingMode]);

  const startCamera = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const constraints = {
        video: {
          facingMode: facingMode,
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      };

      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      setStream(mediaStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      console.error('Error accessing camera:', err);
      setError('Unable to access camera. Please check permissions.');
    } finally {
      setIsLoading(false);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  const capturePhoto = async () => {
    if (!videoRef.current || photos.length >= maxPhotos) return;
    
    setIsCapturing(true);
    
    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      
      // Set canvas dimensions to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      // Draw video frame to canvas
      context.drawImage(video, 0, 0);
      
      // Convert to blob
      canvas.toBlob((blob) => {
        if (blob) {
          const photoUrl = URL.createObjectURL(blob);
          const newPhoto = {
            id: Date.now(),
            url: photoUrl,
            blob: blob,
            timestamp: new Date().toISOString()
          };
          
          setPhotos(prev => [...prev, newPhoto]);
        }
      }, 'image/jpeg', quality);
      
      // Flash effect
      const flashOverlay = document.createElement('div');
      flashOverlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: white;
        z-index: 9999;
        pointer-events: none;
        opacity: 0.8;
        transition: opacity 0.1s ease-out;
      `;
      document.body.appendChild(flashOverlay);
      
      setTimeout(() => {
        flashOverlay.style.opacity = '0';
        setTimeout(() => {
          document.body.removeChild(flashOverlay);
        }, 100);
      }, 50);
      
    } catch (err) {
      console.error('Error capturing photo:', err);
      setError('Failed to capture photo');
    } finally {
      setIsCapturing(false);
    }
  };

  const deletePhoto = (photoId) => {
    setPhotos(prev => {
      const photo = prev.find(p => p.id === photoId);
      if (photo) {
        URL.revokeObjectURL(photo.url);
      }
      return prev.filter(p => p.id !== photoId);
    });
  };

  const switchCamera = () => {
    setFacingMode(prev => prev === 'user' ? 'environment' : 'user');
  };

  const toggleFlash = () => {
    setFlashMode(prev => prev === 'off' ? 'on' : 'off');
  };

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    
    files.forEach(file => {
      if (photos.length < maxPhotos && file.type.startsWith('image/')) {
        const photoUrl = URL.createObjectURL(file);
        const newPhoto = {
          id: Date.now() + Math.random(),
          url: photoUrl,
          blob: file,
          timestamp: new Date().toISOString()
        };
        
        setPhotos(prev => [...prev, newPhoto]);
      }
    });
    
    // Reset file input
    event.target.value = '';
  };

  const handleDone = () => {
    if (photos.length > 0) {
      onCapture(photos);
    }
    handleClose();
  };

  const handleClose = () => {
    // Cleanup photo URLs
    photos.forEach(photo => {
      URL.revokeObjectURL(photo.url);
    });
    setPhotos([]);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black z-50 lg:hidden">
      {/* Camera View */}
      <div className="relative w-full h-full">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black">
            <div className="text-white text-center">
              <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
              <p>Starting camera...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-black">
            <div className="text-white text-center px-4">
              <Camera className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p className="mb-4">{error}</p>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg"
              >
                Upload from Gallery
              </button>
            </div>
          </div>
        )}

        {!error && !isLoading && (
          <>
            {/* Video Stream */}
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />

            {/* Camera Overlay */}
            <div className="absolute inset-0">
              {/* Top Controls */}
              <div className="absolute top-0 left-0 right-0 p-4 bg-gradient-to-b from-black/50 to-transparent">
                <div className="flex items-center justify-between">
                  <button
                    onClick={handleClose}
                    className="p-2 text-white bg-black/30 rounded-full backdrop-blur-sm"
                  >
                    <X className="w-6 h-6" />
                  </button>
                  
                  <div className="text-white text-center">
                    <p className="text-sm">
                      {photos.length}/{maxPhotos} photos
                    </p>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={toggleFlash}
                      className="p-2 text-white bg-black/30 rounded-full backdrop-blur-sm"
                    >
                      {flashMode === 'on' ? <Flash className="w-5 h-5" /> : <FlashOff className="w-5 h-5" />}
                    </button>
                    
                    <button
                      onClick={switchCamera}
                      className="p-2 text-white bg-black/30 rounded-full backdrop-blur-sm"
                    >
                      <RotateCcw className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Center Focus Grid */}
              <div className="absolute inset-0 pointer-events-none">
                <div className="relative w-full h-full">
                  {/* Grid Lines */}
                  <div className="absolute inset-0 grid grid-cols-3 grid-rows-3 opacity-30">
                    {Array.from({ length: 9 }).map((_, i) => (
                      <div key={i} className="border border-white/20" />
                    ))}
                  </div>
                  
                  {/* Center Focus Circle */}
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                    <div className="w-20 h-20 border-2 border-white rounded-full opacity-50"></div>
                  </div>
                </div>
              </div>

              {/* Bottom Controls */}
              <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/50 to-transparent">
                <div className="flex items-center justify-between">
                  {/* Gallery Button */}
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="p-3 text-white bg-black/30 rounded-full backdrop-blur-sm"
                  >
                    <ImageIcon className="w-6 h-6" />
                  </button>

                  {/* Capture Button */}
                  <button
                    onClick={capturePhoto}
                    disabled={isCapturing || photos.length >= maxPhotos}
                    className={`w-16 h-16 rounded-full border-4 border-white backdrop-blur-sm transition-all ${
                      isCapturing 
                        ? 'bg-red-500 scale-95' 
                        : photos.length >= maxPhotos
                        ? 'bg-gray-500 opacity-50'
                        : 'bg-white/20 hover:bg-white/30 active:scale-95'
                    }`}
                  >
                    {isCapturing && (
                      <div className="w-full h-full rounded-full bg-red-600 animate-pulse"></div>
                    )}
                  </button>

                  {/* Done Button */}
                  <button
                    onClick={handleDone}
                    disabled={photos.length === 0}
                    className={`p-3 rounded-full backdrop-blur-sm transition-colors ${
                      photos.length > 0
                        ? 'bg-green-600 text-white'
                        : 'bg-black/30 text-white/50'
                    }`}
                  >
                    <Check className="w-6 h-6" />
                  </button>
                </div>

                {/* Photo Thumbnails */}
                {photos.length > 0 && (
                  <div className="flex justify-center mt-4 space-x-2 overflow-x-auto">
                    {photos.map((photo) => (
                      <div key={photo.id} className="relative flex-shrink-0">
                        <img
                          src={photo.url}
                          alt="Captured"
                          className="w-12 h-12 rounded-lg object-cover border-2 border-white/50"
                        />
                        <button
                          onClick={() => deletePhoto(photo.id)}
                          className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center text-xs"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {/* Hidden Canvas for Photo Capture */}
        <canvas ref={canvasRef} className="hidden" />
        
        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple
          onChange={handleFileUpload}
          className="hidden"
        />
      </div>
    </div>
  );
}

export default MobileCameraCapture;