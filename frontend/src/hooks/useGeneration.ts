import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

// Query keys
export const generationKeys = {
  all: ['generations'] as const,
  bySpec: (specId: string) => [...generationKeys.all, 'spec', specId] as const,
  byId: (generationId: string) => [...generationKeys.all, 'id', generationId] as const,
};

export interface GenerateMCPRequest {
  server_name?: string;
  server_description?: string;
}

export interface GenerateMCPResponse {
  generation_id: string;
  status: string;
  message: string;
  selected_endpoints_count: number;
}

export interface GenerationStatus {
  id: string;
  status: string;
  server_name: string;
  selected_endpoints_count: number;
  error_message?: string;
  created_at: string;
  lines_of_code?: number;
}

export interface GeneratedServer {
  id: string;
  server_name: string;
  status: string;
  selected_endpoints_count: number;
  lines_of_code?: number;
  created_at: string;
  download_count: number;
}

export interface ListGeneratedServersResponse {
  servers: GeneratedServer[];
}

// Generate MCP server
export function useGenerateMCP(specId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: GenerateMCPRequest = {}) => {
      const { data } = await api.post<GenerateMCPResponse>(
        `/swagger-specs/${specId}/generate-mcp`,
        request
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: generationKeys.bySpec(specId) });
    },
  });
}

// Get generation status
export function useGenerationStatus(generationId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: generationKeys.byId(generationId),
    queryFn: async () => {
      const { data } = await api.get<GenerationStatus>(
        `/swagger-specs/generated-servers/${generationId}/status`
      );
      return data;
    },
    enabled: enabled && !!generationId,
    refetchInterval: (query) => {
      // Poll every 2 seconds if status is pending or generating
      const status = query.state.data?.status;
      return status === 'pending' || status === 'generating' ? 2000 : false;
    },
  });
}

// List generated servers for a spec
export function useGeneratedServers(specId: string) {
  return useQuery({
    queryKey: generationKeys.bySpec(specId),
    queryFn: async () => {
      const { data } = await api.get<ListGeneratedServersResponse>(
        `/swagger-specs/${specId}/generated-servers`
      );
      return data;
    },
    enabled: !!specId,
  });
}

// Deploy MCP server
export function useDeployMCP() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (generationId: string) => {
      const { data } = await api.post(
        `/swagger-specs/generated-servers/${generationId}/deploy`
      );
      return data;
    },
    onSuccess: (data, generationId) => {
      queryClient.invalidateQueries({ queryKey: generationKeys.byId(generationId) });
      queryClient.invalidateQueries({ queryKey: ['deployed-servers'] });
    },
  });
}

// Undeploy MCP server
export function useUndeployMCP() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (generationId: string) => {
      const { data } = await api.post(
        `/swagger-specs/generated-servers/${generationId}/undeploy`
      );
      return data;
    },
    onSuccess: (data, generationId) => {
      queryClient.invalidateQueries({ queryKey: generationKeys.byId(generationId) });
      queryClient.invalidateQueries({ queryKey: ['deployed-servers'] });
    },
  });
}

// Delete MCP server
export function useDeleteMCP() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (generationId: string) => {
      await api.delete(`/swagger-specs/generated-servers/${generationId}`);
    },
    onSuccess: (data, generationId) => {
      queryClient.invalidateQueries({ queryKey: generationKeys.byId(generationId) });
      queryClient.invalidateQueries({ queryKey: ['deployed-servers'] });
      queryClient.invalidateQueries({ queryKey: generationKeys.all });
    },
  });
}

// List all deployed MCP servers
export function useDeployedServers() {
  return useQuery({
    queryKey: ['deployed-servers'],
    queryFn: async () => {
      const { data } = await api.get('/swagger-specs/deployed-servers');
      return data;
    },
  });
}

// Get MCP server info
export function useMCPServerInfo(serverId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: ['mcp-server-info', serverId],
    queryFn: async () => {
      const { data } = await api.get(`/mcp/serve/${serverId}/info`);
      return data;
    },
    enabled: enabled && !!serverId,
  });
}

// Download generated server (returns the download URL)
export function getDownloadUrl(generationId: string): string {
  return `/swagger-specs/generated-servers/${generationId}/download`;
}
