import { useState } from 'react';
import { FileCode, Globe, Calendar, Hash, Settings, Edit2, Check, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useUpdateBaseURL } from '@/hooks/useSwaggerSpec';
import type { SwaggerSpec } from '@/types/swagger';

interface SpecViewerProps {
  spec: SwaggerSpec;
}

function SpecViewer({ spec }: SpecViewerProps) {
  const navigate = useNavigate();
  const [isEditingBaseURL, setIsEditingBaseURL] = useState(false);
  const [baseURLInput, setBaseURLInput] = useState(spec.base_url || '');

  const updateBaseURL = useUpdateBaseURL();

  const handleSaveBaseURL = async () => {
    try {
      await updateBaseURL.mutateAsync({
        specId: spec.id,
        baseUrl: baseURLInput,
      });
      setIsEditingBaseURL(false);
      alert('Base URL updated successfully. Deployed MCP servers have been updated.');
    } catch (error) {
      alert('Failed to update base URL. Please try again.');
    }
  };

  const handleCancelEdit = () => {
    setBaseURLInput(spec.base_url || '');
    setIsEditingBaseURL(false);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getMethodColor = (method: string) => {
    const colors: Record<string, string> = {
      GET: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      POST: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      PUT: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
      DELETE: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
      PATCH: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
    };
    return colors[method] || 'bg-gray-100 text-gray-800';
  };

  const getSourceTypeLabel = (sourceType: string) => {
    const labels: Record<string, string> = {
      upload: 'File Upload',
      url: 'URL',
      paste: 'Pasted Content',
      endpoint: 'API Endpoint',
    };
    return labels[sourceType] || sourceType;
  };

  return (
    <div className="space-y-6">
      {/* Spec Information Card */}
      <Card className="border-2 shadow-md">
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2 flex-wrap">
                <CardTitle className="text-3xl font-bold">
                  {spec.title}
                </CardTitle>
                <Badge variant="outline" className="text-sm font-semibold">
                  {spec.spec_version}
                </Badge>
              </div>
              {spec.spec_description && (
                <CardDescription className="mt-2 text-base">
                  {spec.spec_description}
                </CardDescription>
              )}
            </div>
            <Button
              onClick={() => navigate(`/specs/${spec.id}/endpoints`)}
              className="bg-primary hover:bg-primary/90 font-semibold rounded-full shadow-lg shadow-primary/30"
            >
              <Settings className="w-4 h-4 mr-2" />
              Configure Endpoints
            </Button>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Metadata Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-4 p-4 rounded-xl bg-gradient-to-br from-primary/10 to-purple-500/10 border border-primary/20 shadow-md">
              <div className="flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-primary to-purple-600 shadow-lg shadow-primary/30">
                <Hash className="w-7 h-7 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Endpoints</p>
                <p className="text-3xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
                  {spec.total_endpoints}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4 p-4 rounded-xl bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/20 shadow-md">
              <div className="flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 shadow-lg shadow-blue-500/30">
                <Globe className="w-7 h-7 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-muted-foreground">Base URL</p>
                {isEditingBaseURL ? (
                  <div className="flex items-center gap-2 mt-1">
                    <Input
                      type="text"
                      value={baseURLInput}
                      onChange={(e) => setBaseURLInput(e.target.value)}
                      placeholder="https://api.example.com"
                      className="text-sm font-mono h-8"
                    />
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={handleSaveBaseURL}
                      disabled={updateBaseURL.isPending}
                      className="h-8 w-8 p-0"
                    >
                      <Check className="w-4 h-4 text-green-600" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={handleCancelEdit}
                      disabled={updateBaseURL.isPending}
                      className="h-8 w-8 p-0"
                    >
                      <X className="w-4 h-4 text-red-600" />
                    </Button>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-mono truncate font-semibold">
                      {spec.base_url || 'Not set'}
                    </p>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setIsEditingBaseURL(true)}
                      className="h-6 w-6 p-0"
                    >
                      <Edit2 className="w-3 h-3" />
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Additional Info */}
          <div className="flex flex-wrap items-center gap-4 pt-4 border-t text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <FileCode className="w-4 h-4" />
              <span>Source: {getSourceTypeLabel(spec.source_type)}</span>
            </div>
            {spec.source_reference && (
              <div className="flex items-center gap-2">
                <span className="text-xs">({spec.source_reference})</span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              <span>Imported {formatDate(spec.created_at)}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Endpoints Summary */}
      {spec.endpoints_summary?.endpoints && (
        <Card className="border-2 shadow-lg">
          <CardHeader>
            <CardTitle className="text-2xl font-bold">Endpoints Overview</CardTitle>
            <CardDescription className="text-base">
              {spec.total_endpoints} endpoint{spec.total_endpoints !== 1 ? 's' : ''} available
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {spec.endpoints_summary.endpoints.map((endpoint: any, index: number) => (
                <div
                  key={index}
                  className="flex items-center gap-3 p-4 rounded-xl border-2 hover:border-primary/50 hover:shadow-md transition-all duration-200 bg-gradient-to-r from-card to-muted/20"
                >
                  <Badge className={`${getMethodColor(endpoint.method)} font-bold px-3 py-1`} variant="outline">
                    {endpoint.method}
                  </Badge>
                  <code className="flex-1 text-sm font-mono font-semibold">{endpoint.path}</code>
                  {endpoint.summary && (
                    <span className="text-sm text-muted-foreground hidden md:block max-w-xs truncate">
                      {endpoint.summary}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default SpecViewer;
