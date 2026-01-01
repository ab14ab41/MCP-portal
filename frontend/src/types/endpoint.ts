export interface ParameterConfigItem {
  name: string;
  type: string;
  location: 'path' | 'query' | 'header' | 'cookie';
  description: string;
  required: boolean;  // Original from spec
  user_required: boolean;  // User's choice (can override required)
  deprecated: boolean;
  schema: Record<string, any>;
}

export interface EndpointConfig {
  id: string;
  swagger_spec_id: string;
  http_method: string;
  path: string;
  operation_id: string | null;
  is_selected: boolean;
  mcp_tool_name: string | null;
  mcp_description: string | null;
  parameter_configurations: ParameterConfigItem[] | null;
  request_schema: Record<string, any> | null;
  response_schema: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export interface EndpointConfigWithDetails extends EndpointConfig {
  summary: string;
  description: string;
  tags: string[];
  deprecated: boolean;
}

export interface EndpointConfigUpdate {
  is_selected?: boolean;
  mcp_tool_name?: string | null;
  mcp_description?: string | null;
  parameter_configurations?: ParameterConfigItem[] | null;
}

export interface EndpointConfigBatchUpdate {
  endpoint_id: string;
  is_selected: boolean;
  mcp_tool_name?: string | null;
  mcp_description?: string | null;
  parameter_configurations?: ParameterConfigItem[] | null;
}
