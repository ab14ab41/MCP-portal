import { useState } from 'react';
import { Upload, Link, FileText, Loader2 } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import FileUpload from './FileUpload';
import {
  useUploadSwaggerSpec,
  useCreateSpecFromURL,
  useCreateSpecFromContent,
} from '@/hooks/useSwaggerSpec';

interface SpecUploaderProps {
  projectId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

function SpecUploader({ projectId, open, onOpenChange, onSuccess }: SpecUploaderProps) {
  const [selectedTab, setSelectedTab] = useState('file');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [url, setUrl] = useState('');
  const [content, setContent] = useState('');
  const [contentFormat, setContentFormat] = useState<'json' | 'yaml'>('json');

  const uploadFile = useUploadSwaggerSpec();
  const createFromURL = useCreateSpecFromURL();
  const createFromContent = useCreateSpecFromContent();

  const isUploading =
    uploadFile.isPending || createFromURL.isPending || createFromContent.isPending;

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    try {
      await uploadFile.mutateAsync({ projectId, file: selectedFile });
      onSuccess?.();
      handleClose();
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const handleURLSubmit = async () => {
    if (!url) return;

    try {
      await createFromURL.mutateAsync({ project_id: projectId, url });
      onSuccess?.();
      handleClose();
    } catch (error) {
      console.error('Failed to fetch from URL:', error);
    }
  };

  const handleContentSubmit = async () => {
    if (!content) return;

    try {
      await createFromContent.mutateAsync({
        project_id: projectId,
        content,
        format: contentFormat,
      });
      onSuccess?.();
      handleClose();
    } catch (error) {
      console.error('Failed to create from content:', error);
    }
  };

  const handleClose = () => {
    if (!isUploading) {
      setSelectedFile(null);
      setUrl('');
      setContent('');
      setSelectedTab('file');
      onOpenChange(false);
    }
  };

  const handleSubmit = () => {
    switch (selectedTab) {
      case 'file':
        handleFileUpload();
        break;
      case 'url':
        handleURLSubmit();
        break;
      case 'paste':
        handleContentSubmit();
        break;
    }
  };

  const canSubmit = () => {
    switch (selectedTab) {
      case 'file':
        return !!selectedFile;
      case 'url':
        return !!url;
      case 'paste':
        return !!content;
      default:
        return false;
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Import Swagger/OpenAPI Specification</DialogTitle>
          <DialogDescription>
            Choose how you'd like to import your API specification
          </DialogDescription>
        </DialogHeader>

        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="file" className="flex items-center gap-2">
              <Upload className="w-4 h-4" />
              Upload File
            </TabsTrigger>
            <TabsTrigger value="url" className="flex items-center gap-2">
              <Link className="w-4 h-4" />
              From URL
            </TabsTrigger>
            <TabsTrigger value="paste" className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Paste Content
            </TabsTrigger>
          </TabsList>

          <TabsContent value="file" className="space-y-4">
            <FileUpload onFileSelect={setSelectedFile} />
          </TabsContent>

          <TabsContent value="url" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="spec-url">Specification URL</Label>
              <Input
                id="spec-url"
                type="url"
                placeholder="https://api.example.com/openapi.json"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Enter the URL where your OpenAPI specification is hosted
              </p>
            </div>
          </TabsContent>

          <TabsContent value="paste" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="spec-content">Specification Content</Label>
              <div className="flex gap-2 mb-2">
                <Button
                  type="button"
                  variant={contentFormat === 'json' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setContentFormat('json')}
                >
                  JSON
                </Button>
                <Button
                  type="button"
                  variant={contentFormat === 'yaml' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setContentFormat('yaml')}
                >
                  YAML
                </Button>
              </div>
              <Textarea
                id="spec-content"
                placeholder={
                  contentFormat === 'json'
                    ? '{\n  "openapi": "3.0.0",\n  "info": {\n    "title": "My API"\n  }\n}'
                    : 'openapi: 3.0.0\ninfo:\n  title: My API'
                }
                rows={12}
                className="font-mono text-sm"
                value={content}
                onChange={(e) => setContent(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Paste your OpenAPI specification in {contentFormat.toUpperCase()} format
              </p>
            </div>
          </TabsContent>
        </Tabs>

        <div className="flex items-center justify-between pt-4 border-t">
          <div className="text-sm text-muted-foreground">
            Supports OpenAPI 2.0 (Swagger) and 3.0+
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleClose} disabled={isUploading}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={!canSubmit() || isUploading}>
              {isUploading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              {isUploading ? 'Importing...' : 'Import Specification'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default SpecUploader;
