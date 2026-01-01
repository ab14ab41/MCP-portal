import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { API_ENDPOINTS } from '@/constants/api';
import type {
  SwaggerSpec,
  SwaggerSpecWithEndpoints,
  SwaggerSpecFromContent,
  SwaggerSpecFromURL,
} from '@/types/swagger';

// Query keys
export const swaggerSpecKeys = {
  all: ['swagger-specs'] as const,
  lists: () => [...swaggerSpecKeys.all, 'list'] as const,
  listByProject: (projectId: string) => [...swaggerSpecKeys.lists(), projectId] as const,
  details: () => [...swaggerSpecKeys.all, 'detail'] as const,
  detail: (id: string) => [...swaggerSpecKeys.details(), id] as const,
  endpoints: (id: string) => [...swaggerSpecKeys.detail(id), 'endpoints'] as const,
};

// Fetch specs by project
export function useSwaggerSpecs(projectId: string) {
  return useQuery({
    queryKey: swaggerSpecKeys.listByProject(projectId),
    queryFn: async () => {
      const { data } = await api.get<SwaggerSpec[]>(
        `/swagger-specs/project/${projectId}`
      );
      return data;
    },
    enabled: !!projectId,
  });
}

// Fetch single spec
export function useSwaggerSpec(id: string) {
  return useQuery({
    queryKey: swaggerSpecKeys.detail(id),
    queryFn: async () => {
      const { data } = await api.get<SwaggerSpec>(
        API_ENDPOINTS.SWAGGER_SPEC_BY_ID(id)
      );
      return data;
    },
    enabled: !!id,
  });
}

// Fetch spec with endpoints
export function useSwaggerSpecEndpoints(id: string) {
  return useQuery({
    queryKey: swaggerSpecKeys.endpoints(id),
    queryFn: async () => {
      const { data } = await api.get<SwaggerSpecWithEndpoints>(
        `${API_ENDPOINTS.SWAGGER_SPEC_BY_ID(id)}/endpoints`
      );
      return data;
    },
    enabled: !!id,
  });
}

// Upload file mutation
export function useUploadSwaggerSpec() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ projectId, file }: { projectId: string; file: File }) => {
      const formData = new FormData();
      formData.append('project_id', projectId);
      formData.append('file', file);

      const { data } = await api.post<SwaggerSpec>(
        '/swagger-specs/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: swaggerSpecKeys.listByProject(data.project_id),
      });
    },
  });
}

// Create from URL mutation
export function useCreateSpecFromURL() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (specData: SwaggerSpecFromURL) => {
      const { data } = await api.post<SwaggerSpec>(
        '/swagger-specs/from-url',
        specData
      );
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: swaggerSpecKeys.listByProject(data.project_id),
      });
    },
  });
}

// Create from content mutation
export function useCreateSpecFromContent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (specData: SwaggerSpecFromContent) => {
      const { data } = await api.post<SwaggerSpec>(
        '/swagger-specs/from-content',
        specData
      );
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: swaggerSpecKeys.listByProject(data.project_id),
      });
    },
  });
}

// Delete spec mutation
export function useDeleteSwaggerSpec() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(API_ENDPOINTS.SWAGGER_SPEC_BY_ID(id));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: swaggerSpecKeys.lists() });
    },
  });
}

// Update base URL mutation
export function useUpdateBaseURL() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ specId, baseUrl }: { specId: string; baseUrl: string }) => {
      const { data } = await api.patch<SwaggerSpec>(
        `${API_ENDPOINTS.SWAGGER_SPEC_BY_ID(specId)}/base-url`,
        { base_url: baseUrl }
      );
      return data;
    },
    onSuccess: (data) => {
      // Invalidate both the specific spec and the list
      queryClient.invalidateQueries({
        queryKey: swaggerSpecKeys.detail(data.id),
      });
      queryClient.invalidateQueries({
        queryKey: swaggerSpecKeys.listByProject(data.project_id),
      });
    },
  });
}
