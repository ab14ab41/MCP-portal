import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type {
  EndpointConfigWithDetails,
  EndpointConfigUpdate,
  EndpointConfigBatchUpdate,
  EndpointConfig,
} from '@/types/endpoint';

// Query keys
export const endpointConfigKeys = {
  all: ['endpoint-configurations'] as const,
  bySpec: (specId: string) => [...endpointConfigKeys.all, 'spec', specId] as const,
  selected: (specId: string) => [...endpointConfigKeys.all, 'selected', specId] as const,
};

// Initialize endpoint configurations
export function useInitializeEndpointConfigs(specId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const { data } = await api.post<EndpointConfig[]>(
        `/endpoint-configurations/initialize/${specId}`
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: endpointConfigKeys.bySpec(specId) });
    },
  });
}

// Fetch endpoint configurations with details
export function useEndpointConfigs(specId: string) {
  return useQuery({
    queryKey: endpointConfigKeys.bySpec(specId),
    queryFn: async () => {
      const { data } = await api.get<EndpointConfigWithDetails[]>(
        `/endpoint-configurations/swagger-spec/${specId}`
      );
      return data;
    },
    enabled: !!specId,
  });
}

// Fetch only selected configurations
export function useSelectedEndpointConfigs(specId: string) {
  return useQuery({
    queryKey: endpointConfigKeys.selected(specId),
    queryFn: async () => {
      const { data } = await api.get<EndpointConfig[]>(
        `/endpoint-configurations/selected/${specId}`
      );
      return data;
    },
    enabled: !!specId,
  });
}

// Update single endpoint configuration
export function useUpdateEndpointConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data: updateData }: { id: string; data: EndpointConfigUpdate }) => {
      const { data } = await api.put<EndpointConfig>(
        `/endpoint-configurations/${id}`,
        updateData
      );
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: endpointConfigKeys.bySpec(data.swagger_spec_id),
      });
      queryClient.invalidateQueries({
        queryKey: endpointConfigKeys.selected(data.swagger_spec_id),
      });
    },
  });
}

// Batch update endpoint configurations
export function useBatchUpdateEndpointConfigs() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ specId, updates }: { specId: string; updates: EndpointConfigBatchUpdate[] }) => {
      const { data } = await api.post<EndpointConfig[]>(
        '/endpoint-configurations/batch-update',
        updates
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: endpointConfigKeys.bySpec(variables.specId),
      });
      queryClient.invalidateQueries({
        queryKey: endpointConfigKeys.selected(variables.specId),
      });
    },
  });
}
