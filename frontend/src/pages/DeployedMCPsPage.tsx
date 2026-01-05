import { Server, Play, Square, Trash2, ExternalLink, Code, Activity, Info, RotateCw, Power, Search } from 'lucide-react';
import { useState, useMemo } from 'react';
import Header from '@/components/layout/Header';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useDeployedServers, useUndeployMCP, useDeleteMCP } from '@/hooks/useGeneration';
import { useNavigate } from 'react-router-dom';
import { api, getBackendUrl } from '@/lib/api';

function DeployedMCPsPage() {
  const navigate = useNavigate();
  const { data: deployedData, isLoading, refetch } = useDeployedServers();
  const undeployMCP = useUndeployMCP();
  const deleteMCP = useDeleteMCP();
  const [infoModalServer, setInfoModalServer] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const allServers = deployedData?.servers || [];

  // Filter servers based on search query
  const servers = useMemo(() => {
    if (!searchQuery.trim()) return allServers;

    const query = searchQuery.toLowerCase();
    return allServers.filter((server: any) =>
      server.project_name?.toLowerCase().includes(query) ||
      server.server_name?.toLowerCase().includes(query) ||
      server.base_url?.toLowerCase().includes(query)
    );
  }, [allServers, searchQuery]);

  const handleStop = async (serverId: string, serverName: string) => {
    if (!confirm(`Are you sure you want to stop "${serverName}"?`)) {
      return;
    }

    try {
      await undeployMCP.mutateAsync(serverId);
      alert('MCP server stopped successfully');
    } catch (error) {
      console.error('Failed to stop MCP:', error);
      alert('Failed to stop MCP server. Please try again.');
    }
  };

  const handleStart = async (serverId: string, serverName: string) => {
    try {
      await api.post(`/swagger-specs/generated-servers/${serverId}/deploy`);
      await refetch();
      alert('MCP server started successfully');
    } catch (error) {
      console.error('Failed to start MCP:', error);
      alert('Failed to start MCP server. Please try again.');
    }
  };

  const handleRestart = async (serverId: string, serverName: string) => {
    try {
      // Stop then re-deploy
      await undeployMCP.mutateAsync(serverId);
      // Wait a moment
      await new Promise(resolve => setTimeout(resolve, 1000));
      // Re-deploy by calling the deploy endpoint
      await api.post(`/swagger-specs/generated-servers/${serverId}/deploy`);
      await refetch();
      alert('MCP server restarted successfully');
    } catch (error) {
      console.error('Failed to restart MCP:', error);
      alert('Failed to restart MCP server. Please try again.');
    }
  };

  const handleDelete = async (serverId: string, serverName: string) => {
    if (!confirm(`Are you sure you want to permanently delete "${serverName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await deleteMCP.mutateAsync(serverId);
      alert('MCP server deleted successfully');
    } catch (error) {
      console.error('Failed to delete MCP:', error);
      alert('Failed to delete MCP server. Please try again.');
    }
  };

  const handleViewInfo = async (server: any) => {
    try {
      const { data } = await api.get(`/mcp/serve/${server.id}/info`);
      setInfoModalServer({ ...server, info: data });
    } catch (error) {
      console.error('Failed to fetch MCP info:', error);
      alert('Failed to fetch MCP info. Please try again.');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto px-6 py-8">
          <p>Loading...</p>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-6 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-lg">
              <Server className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold tracking-tight">Deployment</h1>
              <p className="text-muted-foreground">Manage your MCP server deployments</p>
            </div>
          </div>

          <div className="flex items-center gap-4 mt-6 flex-wrap">
            <Badge variant="secondary" className="px-4 py-2 text-base font-semibold">
              <Activity className="w-4 h-4 mr-2" />
              {servers.length} {servers.length === 1 ? 'Server' : 'Servers'}
            </Badge>
            <div className="flex-1 max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Search servers..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Servers Grid */}
        {servers.length === 0 ? (
          <Card className="border-2 border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-16">
              <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
                <Server className="w-8 h-8 text-muted-foreground" />
              </div>
              {searchQuery ? (
                <>
                  <h3 className="text-xl font-semibold mb-2">No Results Found</h3>
                  <p className="text-muted-foreground text-center mb-6">
                    No servers match "{searchQuery}"
                  </p>
                  <Button onClick={() => setSearchQuery('')} variant="outline" className="rounded-full">
                    Clear Search
                  </Button>
                </>
              ) : (
                <>
                  <h3 className="text-xl font-semibold mb-2">No Deployments</h3>
                  <p className="text-muted-foreground text-center mb-6">
                    Deploy your first MCP server to get started
                  </p>
                  <Button onClick={() => navigate('/projects')} className="rounded-full">
                    Go to Projects
                  </Button>
                </>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {servers.map((server: any) => (
              <Card key={server.id} className="border-2 hover:border-primary/50 transition-all">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-xl font-extrabold mb-2">{server.project_name}</CardTitle>
                      <CardDescription className="mb-2">
                        {server.server_name}
                      </CardDescription>
                      <div className="flex items-center gap-2">
                        <Badge
                          variant={server.is_active ? 'default' : 'secondary'}
                          className="font-semibold"
                        >
                          {server.is_active ? (
                            <>
                              <Play className="w-3 h-3 mr-1" />
                              Active
                            </>
                          ) : (
                            <>
                              <Square className="w-3 h-3 mr-1" />
                              Inactive
                            </>
                          )}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-secondary/50 rounded-lg p-3">
                      <p className="text-xs text-muted-foreground mb-1">Endpoints</p>
                      <p className="text-lg font-bold">{server.selected_endpoints_count}</p>
                    </div>
                    <div className="bg-secondary/50 rounded-lg p-3">
                      <p className="text-xs text-muted-foreground mb-1">Lines</p>
                      <p className="text-lg font-bold">{server.lines_of_code || 0}</p>
                    </div>
                  </div>

                  {/* API Details */}
                  <div className="space-y-2">
                    <div className="text-xs text-muted-foreground">Base URL:</div>
                    <div className="flex items-center gap-2">
                      <code className="text-xs bg-secondary rounded px-2 py-1 flex-1 truncate">
                        {server.base_url || 'N/A'}
                      </code>
                    </div>
                  </div>

                  {/* MCP Endpoint */}
                  <div className="space-y-2">
                    <div className="text-xs text-muted-foreground">MCP Endpoint:</div>
                    <div className="flex items-center gap-2">
                      <code className="text-xs bg-secondary rounded px-2 py-1 flex-1 truncate">
                        {getBackendUrl()}{server.deployment_url}
                      </code>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-7 w-7 p-0"
                        onClick={() => copyToClipboard(`${getBackendUrl()}${server.deployment_url}`)}
                        title="Copy endpoint URL"
                      >
                        <Code className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>

                  {/* Deployment Time */}
                  <div className="text-xs text-muted-foreground pt-2 border-t">
                    Deployed: {formatDate(server.deployed_at)}
                  </div>

                  {/* Actions */}
                  <div className="space-y-2 pt-2">
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex-1"
                        onClick={() => navigate(`/projects/${server.project_id}`)}
                        title="View Project"
                      >
                        <ExternalLink className="w-3 h-3 mr-2" />
                        Project
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleViewInfo(server)}
                        title="View MCP Info"
                      >
                        <Info className="w-3 h-3" />
                      </Button>
                    </div>
                    <div className="flex gap-2">
                      {server.is_active ? (
                        <Button
                          size="sm"
                          variant="outline"
                          className="flex-1"
                          onClick={() => handleStop(server.id, server.server_name)}
                          disabled={undeployMCP.isPending}
                          title="Stop MCP Server (makes it inactive but doesn't delete)"
                        >
                          <Power className="w-3 h-3 mr-2" />
                          Stop
                        </Button>
                      ) : (
                        <Button
                          size="sm"
                          variant="default"
                          className="flex-1"
                          onClick={() => handleStart(server.id, server.server_name)}
                          title="Start MCP Server"
                        >
                          <Play className="w-3 h-3 mr-2" />
                          Start
                        </Button>
                      )}
                      {server.is_active && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleRestart(server.id, server.server_name)}
                          disabled={undeployMCP.isPending}
                          title="Restart MCP Server"
                        >
                          <RotateCw className="w-3 h-3" />
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDelete(server.id, server.server_name)}
                        disabled={deleteMCP.isPending}
                        title="Permanently delete MCP Server"
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Info Modal */}
        {infoModalServer && (
          <div
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setInfoModalServer(null)}
          >
            <Card
              className="w-full max-w-3xl max-h-[90vh] overflow-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-2xl font-bold">{infoModalServer.server_name}</CardTitle>
                    <CardDescription className="mt-1">MCP Server Information</CardDescription>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setInfoModalServer(null)}
                  >
                    ✕
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {infoModalServer.info ? (
                  <>
                    <div>
                      <h3 className="font-semibold mb-2">Base URL</h3>
                      <code className="text-sm bg-secondary rounded px-3 py-2 block">
                        {infoModalServer.info.base_url}
                      </code>
                    </div>
                    <div>
                      <h3 className="font-semibold mb-2">Server ID</h3>
                      <code className="text-sm bg-secondary rounded px-3 py-2 block">
                        {infoModalServer.info.server_id}
                      </code>
                    </div>
                    <div>
                      <h3 className="font-semibold mb-2">Registered At</h3>
                      <p className="text-sm">{formatDate(infoModalServer.info.registered_at)}</p>
                    </div>
                    <div>
                      <h3 className="font-semibold mb-2">Available Tools ({infoModalServer.info.tools_count})</h3>
                      <div className="space-y-3 max-h-96 overflow-auto">
                        {infoModalServer.info.tools?.map((tool: any, idx: number) => (
                          <div key={idx} className="border rounded-lg p-3 bg-secondary/30">
                            <div className="font-mono font-semibold text-sm mb-1">{tool.name}</div>
                            <div className="text-sm text-muted-foreground mb-2">{tool.description}</div>
                            <details className="text-xs">
                              <summary className="cursor-pointer font-semibold mb-2">Input Schema</summary>
                              <pre className="bg-background rounded p-2 overflow-auto">
                                {JSON.stringify(tool.inputSchema, null, 2)}
                              </pre>
                            </details>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                ) : (
                  <p>Loading...</p>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}

export default DeployedMCPsPage;
