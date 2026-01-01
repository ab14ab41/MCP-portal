export interface SwaggerSpec {
  id: string;
  project_id: string;
  spec_version: string;
  title: string;
  spec_description: string | null;
  base_url: string | null;
  source_type: 'upload' | 'url' | 'paste' | 'endpoint';
  source_reference: string | null;
  total_endpoints: number;
  endpoints_summary: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export interface EndpointParameter {
  name: string;
  location: 'path' | 'query' | 'header' | 'cookie';
  description: string;
  required: boolean;
  deprecated: boolean;
  schema: Record<string, any>;
}

export interface Endpoint {
  method: string;
  path: string;
  operation_id: string | null;
  summary: string;
  description: string;
  tags: string[];
  parameters: EndpointParameter[];
  request_body: Record<string, any> | null;
  responses: Record<string, any>;
  deprecated: boolean;
}

export interface SwaggerSpecWithEndpoints extends SwaggerSpec {
  endpoints: Endpoint[];
}

export interface SwaggerSpecFromContent {
  project_id: string;
  content: string;
  format: 'json' | 'yaml';
}

export interface SwaggerSpecFromURL {
  project_id: string;
  url: string;
}

export interface ValidationResult {
  valid: boolean;
  version: string | null;
  errors: string[] | null;
  warnings: string[] | null;
}
