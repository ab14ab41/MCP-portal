import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { API_ENDPOINTS } from '@/constants/api';
import type { Project, ProjectWithStats, ProjectCreate, ProjectUpdate } from '@/types/project';

// Query keys
export const projectKeys = {
  all: ['projects'] as const,
  lists: () => [...projectKeys.all, 'list'] as const,
  list: (filters: { search?: string; skip?: number; limit?: number }) =>
    [...projectKeys.lists(), filters] as const,
  details: () => [...projectKeys.all, 'detail'] as const,
  detail: (id: string) => [...projectKeys.details(), id] as const,
};

// Fetch all projects
export function useProjects(params?: { search?: string; skip?: number; limit?: number }) {
  return useQuery({
    queryKey: projectKeys.list(params || {}),
    queryFn: async () => {
      const { data } = await api.get<Project[]>(API_ENDPOINTS.PROJECTS, { params });
      return data;
    },
  });
}

// Fetch single project with stats
export function useProject(id: string) {
  return useQuery({
    queryKey: projectKeys.detail(id),
    queryFn: async () => {
      const { data } = await api.get<ProjectWithStats>(API_ENDPOINTS.PROJECT_BY_ID(id));
      return data;
    },
    enabled: !!id,
  });
}

// Create project mutation
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (projectData: ProjectCreate) => {
      const { data } = await api.post<Project>(API_ENDPOINTS.PROJECTS, projectData);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
    },
  });
}

// Update project mutation
export function useUpdateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data: projectData }: { id: string; data: ProjectUpdate }) => {
      const { data } = await api.put<Project>(API_ENDPOINTS.PROJECT_BY_ID(id), projectData);
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
      queryClient.invalidateQueries({ queryKey: projectKeys.detail(data.id) });
    },
  });
}

// Delete project mutation
export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(API_ENDPOINTS.PROJECT_BY_ID(id));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
    },
  });
}
