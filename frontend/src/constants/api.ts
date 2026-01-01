export const API_ENDPOINTS = {
  PROJECTS: '/projects',
  PROJECT_BY_ID: (id: string) => `/projects/${id}`,
  SWAGGER_SPECS: '/swagger-specs',
  SWAGGER_SPEC_BY_ID: (id: string) => `/swagger-specs/${id}`,
  ENDPOINT_CONFIGURATIONS: (specId: string) => `/swagger-specs/${specId}/endpoint-configurations`,
  GENERATE_MCP: (specId: string) => `/swagger-specs/${specId}/generate-mcp`,
  GENERATED_SERVER: (id: string) => `/generated-servers/${id}`,
} as const;
