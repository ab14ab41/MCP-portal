import { useMutation, useQuery } from '@tanstack/react-query';
import api from '@/lib/api';

interface Tool {
  name: string;
  description: string;
  input_schema: {
    type: string;
    properties: Record<string, any>;
    required: string[];
  };
}

interface ToolsResponse {
  server_id: string;
  server_name: string;
  tools: Tool[];
  tool_count: number;
}

interface TestMessageRequest {
  message: string;
  conversation_history?: any[];
  provider?: string;
  model?: string;
  api_key?: string;
  base_url?: string;
  server_ids?: string[];
  custom_tools?: any[];
}

interface ToolCall {
  id: string;
  name: string;
  input: Record<string, any>;
}

interface TestMessageResponse {
  response: string;
  tool_calls: ToolCall[];
  conversation_history: any[];
  stop_reason: string;
  usage: {
    input_tokens: number;
    output_tokens: number;
  };
  requires_tool_execution: boolean;
}

interface ToolExecutionRequest {
  tool_call: ToolCall;
  conversation_history: any[];
  provider?: string;
  model?: string;
  api_key?: string;
  base_url?: string;
  server_ids?: string[];
  custom_tools?: any[];
}

interface ToolExecutionResponse {
  response: string;
  tool_execution_result: any;
  additional_tool_calls: ToolCall[];
  conversation_history: any[];
  stop_reason: string;
  usage: {
    input_tokens: number;
    output_tokens: number;
  };
}

export function useServerTools(serverId: string, enabled: boolean = true) {
  return useQuery<ToolsResponse>({
    queryKey: ['server-tools', serverId],
    queryFn: async () => {
      const response = await api.get(`/ai-testing/deployed-servers/${serverId}/tools`);
      return response.data;
    },
    enabled: enabled && !!serverId
  });
}

export function useTestWithAI(serverId: string) {
  return useMutation<TestMessageResponse, Error, TestMessageRequest>({
    mutationFn: async (data) => {
      const response = await api.post(
        `/ai-testing/deployed-servers/${serverId}/test`,
        data
      );
      return response.data;
    }
  });
}

export function useExecuteTool(serverId: string) {
  return useMutation<ToolExecutionResponse, Error, ToolExecutionRequest>({
    mutationFn: async (data) => {
      const response = await api.post(
        `/ai-testing/deployed-servers/${serverId}/execute-tool`,
        data
      );
      return response.data;
    }
  });
}
