import React, { useState, useRef } from 'react';
import { Upload, X, Image as ImageIcon, AlertCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import { marketplaceAPI } from '../../services/api';
import { useToast } from '../../hooks/use-toast';
import { getImageUrl } from '../../utils/helpers';

const ImageUploader = ({ onImagesChange, maxImages = 5, existingImages = [] }) => {
  const [images, setImages] = useState(existingImages);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);
  const { toast } = useToast();

  const handleImageUpload = async (files) => {
    if (!files || files.length === 0) return;

    const validFiles = Array.from(files).filter(file => {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        toast({
          title: "Invalid File",
          description: `${file.name} is not an image file`,
          variant: "destructive"
        });
        return false;
      }

      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        toast({
          title: "File Too Large",
          description: `${file.name} is larger than 10MB`,
          variant: "destructive"
        });
        return false;
      }

      return true;
    });

    if (validFiles.length === 0) return;

    // Check if we're exceeding max images
    if (images.length + validFiles.length > maxImages) {
      toast({
        title: "Too Many Images",
        description: `Maximum ${maxImages} images allowed`,
        variant: "destructive"
      });
      return;
    }

    setUploading(true);

    try {
      const uploadPromises = validFiles.map(async (file) => {
        const uploadResponse = await marketplaceAPI.uploadImage(file);
        return {
          id: Date.now() + Math.random(), // Temporary ID
          url: uploadResponse.data.image_url,
          file: file,
          name: file.name,
          size: file.size
        };
      });

      const uploadedImages = await Promise.all(uploadPromises);
      const newImages = [...images, ...uploadedImages];
      
      setImages(newImages);
      onImagesChange(newImages);

      toast({
        title: "Success",
        description: `${uploadedImages.length} image(s) uploaded successfully`
      });

    } catch (error) {
      console.error('Error uploading images:', error);
      toast({
        title: "Upload Failed",
        description: "Failed to upload images. Please try again.",
        variant: "destructive"
      });
    } finally {
      setUploading(false);
    }
  };

  const handleRemoveImage = (imageId) => {
    const newImages = images.filter(img => img.id !== imageId);
    setImages(newImages);
    onImagesChange(newImages);

    toast({
      title: "Image Removed",
      description: "Image has been removed from the listing"
    });
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer?.files;
    if (files) {
      handleImageUpload(files);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <Card 
        className={`border-2 border-dashed transition-colors cursor-pointer ${
          dragActive 
            ? 'border-purple-400 bg-purple-50' 
            : 'border-slate-300 hover:border-purple-300'
        }`}
        onClick={() => fileInputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <CardContent className="p-8 text-center">
          {uploading ? (
            <div className="space-y-4">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
              <p className="text-slate-600">Uploading images...</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="mx-auto w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center">
                <Upload className="h-8 w-8 text-purple-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">Upload Product Images</h3>
                <p className="text-slate-600 mb-4">
                  Drag and drop your images here, or click to browse
                </p>
                <div className="text-sm text-slate-500 space-y-1">
                  <p>• Maximum {maxImages} images ({maxImages - images.length} remaining)</p>
                  <p>• Supports: JPG, PNG, GIF</p>
                  <p>• Maximum file size: 10MB per image</p>
                </div>
              </div>
              <Button 
                type="button"
                variant="outline" 
                className="border-purple-200 text-purple-600 hover:bg-purple-50"
              >
                <ImageIcon className="h-4 w-4 mr-2" />
                Choose Images
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        onChange={(e) => handleImageUpload(e.target.files)}
        className="hidden"
      />

      {/* Image Preview Grid */}
      {images.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {images.map((image, index) => (
            <Card key={image.id} className="relative group">
              <CardContent className="p-2">
                <div className="aspect-square relative overflow-hidden rounded-lg">
                  <img
                    src={getImageUrl(image.url)}
                    alt={image.name || `Product image ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                  
                  {/* Remove Button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemoveImage(image.id);
                    }}
                    className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                  >
                    <X className="h-4 w-4" />
                  </button>

                  {/* Primary Badge */}
                  {index === 0 && (
                    <div className="absolute top-2 left-2 bg-purple-600 text-white text-xs px-2 py-1 rounded">
                      Primary
                    </div>
                  )}
                </div>
                
                {/* Image Info */}
                <div className="mt-2 text-xs text-slate-500">
                  <p className="truncate">{image.name}</p>
                  <p>{formatFileSize(image.size)}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Image Guidelines */}
      {images.length === 0 && (
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="text-sm">
                <h4 className="font-medium text-blue-900 mb-2">Image Guidelines</h4>
                <ul className="text-blue-700 space-y-1">
                  <li>• Use high-quality, well-lit photos</li>
                  <li>• Show your item from multiple angles</li>
                  <li>• The first image will be your main product photo</li>
                  <li>• Avoid watermarks or text overlays</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ImageUploader;