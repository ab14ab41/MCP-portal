import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Save, Loader2, Filter, CheckCircle2, Sparkles, Download } from 'lucide-react';
import Header from '@/components/layout/Header';
import EndpointCard from '@/components/endpoints/EndpointCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useSwaggerSpec } from '@/hooks/useSwaggerSpec';
import { useEndpointConfigs, useBatchUpdateEndpointConfigs } from '@/hooks/useEndpointConfig';
import { useGenerateMCP, useGenerationStatus, useDeployMCP } from '@/hooks/useGeneration';
import type { EndpointConfigWithDetails, EndpointConfigBatchUpdate } from '@/types/endpoint';
import { getBackendUrl } from '@/lib/api';

function EndpointSelectionPage() {
  const { specId } = useParams<{ specId: string }>();
  const navigate = useNavigate();

  const { data: spec, isLoading: isSpecLoading } = useSwaggerSpec(specId || '');
  const { data: configs, isLoading: isConfigsLoading } = useEndpointConfigs(specId || '');
  const batchUpdate = useBatchUpdateEndpointConfigs();
  const generateMCP = useGenerateMCP(specId || '');
  const deployMCP = useDeployMCP();

  const [localConfigs, setLocalConfigs] = useState<EndpointConfigWithDetails[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterMethod, setFilterMethod] = useState<string | null>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [generationId, setGenerationId] = useState<string | null>(null);
  const [deploymentUrl, setDeploymentUrl] = useState<string | null>(null);

  // Poll generation status if we have a generation ID
  const { data: generationStatus } = useGenerationStatus(
    generationId || '',
    !!generationId
  );

  // Initialize local state with fetched configs
  useEffect(() => {
    if (configs && !hasChanges) {
      setLocalConfigs(configs);
    }
  }, [configs, hasChanges]);

  const handleConfigChange = (updatedConfig: EndpointConfigWithDetails) => {
    setLocalConfigs((prev) =>
      prev.map((config) => (config.id === updatedConfig.id ? updatedConfig : config))
    );
    setHasChanges(true);
  };

  const handleSave = async () => {
    if (!specId) return;

    // Validate that all selected endpoints have descriptions
    const selectedWithoutDesc = localConfigs.filter(
      c => c.is_selected && !c.mcp_description
    );

    if (selectedWithoutDesc.length > 0) {
      const endpointNames = selectedWithoutDesc.map(c => `${c.http_method} ${c.path}`).join(', ');
      alert(`Please provide descriptions for all selected endpoints:\n\n${endpointNames}`);
      return;
    }

    // Prepare batch updates
    const updates: EndpointConfigBatchUpdate[] = localConfigs.map((config) => ({
      endpoint_id: config.id,
      is_selected: config.is_selected,
      mcp_tool_name: config.mcp_tool_name,
      mcp_description: config.mcp_description,
      parameter_configurations: config.parameter_configurations || null,
    }));

    try {
      await batchUpdate.mutateAsync({ specId, updates });
      setHasChanges(false);
    } catch (error: any) {
      console.error('Failed to save configurations:', error);
      const errorMessage = error?.response?.data?.detail || 'Failed to save configurations. Please try again.';
      alert(errorMessage);
    }
  };

  const handleGenerateMCP = async () => {
    try {
      const result = await generateMCP.mutateAsync({
        server_name: spec?.title,
        server_description: spec?.spec_description
      });
      setGenerationId(result.generation_id);
    } catch (error) {
      console.error('Failed to generate MCP server:', error);
      alert('Failed to generate MCP server. Please try again.');
    }
  };

  const handleDeploy = async () => {
    if (generationId) {
      try {
        const result = await deployMCP.mutateAsync(generationId);
        setDeploymentUrl(result.deployment_url);
      } catch (error: any) {
        console.error('Failed to deploy MCP server:', error);
        const errorMessage = error?.response?.data?.detail || 'Failed to deploy MCP server. Please try again.';
        alert(errorMessage);
      }
    }
  };

  // Filter endpoints
  const filteredConfigs = localConfigs.filter((config) => {
    const matchesSearch =
      config.path.toLowerCase().includes(searchQuery.toLowerCase()) ||
      config.summary.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesMethod = !filterMethod || config.http_method === filterMethod;
    return matchesSearch && matchesMethod;
  });

  const selectedCount = localConfigs.filter((c) => c.is_selected).length;
  const methods = Array.from(new Set(localConfigs.map((c) => c.http_method)));

  if (isSpecLoading || isConfigsLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary" />
            <p className="text-muted-foreground mt-4">Loading configuration...</p>
          </div>
        </main>
      </div>
    );
  }

  if (!spec || !configs) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="text-center py-12">
            <p className="text-destructive">Specification not found</p>
            <Button onClick={() => navigate(-1)} className="mt-4">
              Go Back
            </Button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-6 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-10">
          <Button variant="ghost" onClick={() => navigate(-1)} className="mb-6">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>

          <div className="flex items-start justify-between gap-6">
            <div>
              <h1 className="text-5xl font-bold mb-3 tracking-tight">
                Configure Endpoints
              </h1>
              <p className="text-xl text-muted-foreground mb-4">{spec.title}</p>
              <div className="flex items-center gap-3">
                <Badge variant="secondary" className="px-3 py-1 text-sm font-semibold">
                  {selectedCount} / {localConfigs.length} selected
                </Badge>
                <Badge variant="outline" className="px-3 py-1 text-sm font-semibold">
                  {spec.spec_version}
                </Badge>
              </div>
            </div>
            <Button
              onClick={handleSave}
              disabled={!hasChanges || batchUpdate.isPending}
              size="lg"
              className="h-12 px-8 bg-primary hover:bg-primary/90 font-semibold rounded-full shadow-lg shadow-primary/30"
            >
              {batchUpdate.isPending ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-5 h-5 mr-2" />
                  Save Configuration
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4 mb-8">
          <div className="relative flex-1 max-w-md">
            <Input
              type="text"
              placeholder="Search endpoints..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-12 bg-background border-2 rounded-xl"
            />
          </div>
          <div className="flex items-center gap-2 p-1 rounded-xl bg-secondary/50">
            <Filter className="w-4 h-4 text-muted-foreground ml-2" />
            <Button
              variant={filterMethod === null ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setFilterMethod(null)}
              className={filterMethod === null ? 'bg-primary hover:bg-primary/90 rounded-lg' : 'rounded-lg'}
            >
              All
            </Button>
            {methods.map((method) => (
              <Button
                key={method}
                variant={filterMethod === method ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setFilterMethod(method)}
                className={filterMethod === method ? 'bg-primary hover:bg-primary/90 rounded-lg' : 'rounded-lg'}
              >
                {method}
              </Button>
            ))}
          </div>
        </div>

        {/* Info Banner */}
        {selectedCount > 0 && (
          <div className="mb-8 p-5 rounded-2xl bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800/50">
            <div className="flex items-start gap-4">
              <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10">
                <CheckCircle2 className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="font-semibold text-lg mb-1">
                  {selectedCount} endpoint(s) selected
                </p>
                <p className="text-sm text-muted-foreground">
                  Provide descriptions for all selected endpoints and configure their parameters.
                  You can override whether parameters are mandatory or optional.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Endpoints List */}
        {filteredConfigs.length > 0 ? (
          <div className="space-y-4">
            {filteredConfigs.map((config) => (
              <EndpointCard
                key={config.id}
                endpoint={config}
                onChange={handleConfigChange}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No endpoints match your search</p>
          </div>
        )}

        {/* Save Changes Banner */}
        {hasChanges && (
          <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 z-50">
            <div className="bg-card/95 backdrop-blur-xl border shadow-2xl rounded-2xl px-8 py-4 flex items-center gap-6">
              <p className="text-base font-semibold">You have unsaved changes</p>
              <Button
                onClick={handleSave}
                disabled={batchUpdate.isPending}
                className="bg-primary hover:bg-primary/90 rounded-full"
              >
                {batchUpdate.isPending ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-5 h-5 mr-2" />
                    Save Changes
                  </>
                )}
              </Button>
            </div>
          </div>
        )}

        {/* Generate MCP Button - shown when configurations are saved */}
        {!hasChanges && selectedCount > 0 && !generationStatus && (
          <div className="fixed bottom-8 right-8 z-50">
            <Button
              onClick={handleGenerateMCP}
              disabled={generateMCP.isPending}
              size="lg"
              className="h-14 px-8 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-full shadow-2xl shadow-green-600/30"
            >
              {generateMCP.isPending ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5 mr-2" />
                  Generate MCP Server
                </>
              )}
            </Button>
          </div>
        )}

        {/* Generation Status & Deploy Button */}
        {generationStatus && !deploymentUrl && (
          <div className="fixed bottom-8 right-8 z-50">
            {generationStatus.status === 'completed' ? (
              <Button
                onClick={handleDeploy}
                disabled={deployMCP.isPending}
                size="lg"
                className="h-14 px-8 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-full shadow-2xl shadow-green-600/30"
              >
                {deployMCP.isPending ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Deploying...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 mr-2" />
                    Deploy MCP Server
                  </>
                )}
              </Button>
            ) : generationStatus.status === 'failed' ? (
              <div className="bg-red-50 dark:bg-red-950/30 border-2 border-red-200 dark:border-red-800 rounded-2xl px-6 py-4">
                <p className="text-red-700 dark:text-red-400 font-semibold">Generation Failed</p>
                {generationStatus.error_message && (
                  <p className="text-sm text-red-600 dark:text-red-500 mt-1">{generationStatus.error_message}</p>
                )}
                <Button
                  onClick={() => setGenerationId(null)}
                  size="sm"
                  variant="outline"
                  className="mt-3"
                >
                  Try Again
                </Button>
              </div>
            ) : (
              <div className="bg-card/95 backdrop-blur-xl border shadow-2xl rounded-2xl px-8 py-4">
                <div className="flex items-center gap-3">
                  <Loader2 className="w-5 h-5 animate-spin text-primary" />
                  <div>
                    <p className="font-semibold">Generating MCP Server...</p>
                    <p className="text-sm text-muted-foreground">{generationStatus.selected_endpoints_count} endpoint(s)</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Deployment Success */}
        {deploymentUrl && (
          <div className="fixed bottom-8 right-8 z-50">
            <div className="bg-green-50 dark:bg-green-950/30 border-2 border-green-200 dark:border-green-800 rounded-2xl px-8 py-6 max-w-md">
              <div className="flex items-start gap-4">
                <CheckCircle2 className="w-6 h-6 text-green-600 dark:text-green-400 mt-1 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-lg font-semibold text-green-800 dark:text-green-300 mb-2">MCP Server Deployed!</p>
                  <p className="text-sm text-green-700 dark:text-green-400 mb-3">
                    Your MCP server is now live and accessible.
                  </p>
                  <div className="bg-white dark:bg-gray-900 rounded-lg p-3 mb-3">
                    <p className="text-xs text-muted-foreground mb-1">Endpoint URL:</p>
                    <code className="text-xs font-mono break-all">{getBackendUrl()}{deploymentUrl}</code>
                  </div>
                  <Button
                    onClick={() => navigate('/deployed-mcps')}
                    size="sm"
                    className="w-full bg-green-600 hover:bg-green-700 text-white rounded-full"
                  >
                    View All Deployed MCPs
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default EndpointSelectionPage;
