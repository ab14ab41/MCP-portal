import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Sparkles, AlertCircle, Wrench, Settings, ChevronDown, ChevronUp, Search } from 'lucide-react';
import Header from '@/components/layout/Header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useDeployedServers } from '@/hooks/useGeneration';
import { useServerTools, useTestWithAI, useExecuteTool } from '@/hooks/useAITesting';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  toolCalls?: any[];
  toolResults?: any[];
  usage?: { input_tokens: number; output_tokens: number };
}

function AITestingPage() {
  const { data: deployedData, isLoading: isLoadingServers } = useDeployedServers();
  const [selectedServerIds, setSelectedServerIds] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [conversationHistory, setConversationHistory] = useState<any[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // AI Provider Configuration
  const [provider, setProvider] = useState<'anthropic' | 'openai'>('anthropic');
  const [anthropicModel, setAnthropicModel] = useState('claude-3-haiku-20240307');
  const [anthropicApiKey, setAnthropicApiKey] = useState('');
  const [openaiModel, setOpenaiModel] = useState('gpt-4o');
  const [openaiApiKey, setOpenaiApiKey] = useState('');
  const [openaiBaseUrl, setOpenaiBaseUrl] = useState('https://api.openai.com/v1');
  const [showConfig, setShowConfig] = useState(false);
  const [authorization, setAuthorization] = useState('');

  const allServers = deployedData?.servers || [];

  // Filter servers based on search query
  const servers = allServers.filter((server: any) => {
    if (!searchQuery.trim()) return true;
    const query = searchQuery.toLowerCase();
    return (
      server.project_name?.toLowerCase().includes(query) ||
      server.server_name?.toLowerCase().includes(query)
    );
  });

  const selectedServers = allServers.filter((s: any) => selectedServerIds.includes(s.id));

  // Calculate total tool count from selected servers
  const totalToolCount = selectedServers.reduce((sum: number, server: any) =>
    sum + (server.selected_endpoints_count || 0), 0
  );

  // Use first server ID for API calls (backend will combine tools from all selected servers)
  const primaryServerId = selectedServerIds[0] || '';
  const testWithAI = useTestWithAI(primaryServerId);
  const executeTool = useExecuteTool(primaryServerId);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleToggleServer = (serverId: string) => {
    setSelectedServerIds(prev => {
      if (prev.includes(serverId)) {
        return prev.filter(id => id !== serverId);
      } else {
        return [...prev, serverId];
      }
    });
  };

  const handleClearChat = () => {
    setMessages([]);
    setConversationHistory([]);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || selectedServerIds.length === 0) return;

    const userMessage: Message = {
      role: 'user',
      content: inputMessage
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    try {
      const result = await testWithAI.mutateAsync({
        message: inputMessage,
        conversation_history: conversationHistory,
        provider: provider,
        model: provider === 'openai' ? openaiModel : anthropicModel,
        api_key: provider === 'openai' ? (openaiApiKey || undefined) : (anthropicApiKey || undefined),
        base_url: provider === 'openai' ? openaiBaseUrl : undefined,
        server_ids: selectedServerIds,
        authorization: authorization || undefined
      });

      // Update conversation history
      setConversationHistory(result.conversation_history);

      // Add assistant's response to messages
      const assistantMessage: Message = {
        role: 'assistant',
        content: result.response || '(Tool calls in progress...)',
        toolCalls: result.tool_calls,
        usage: result.usage
      };

      setMessages(prev => [...prev, assistantMessage]);

      // If tools need to be executed
      if (result.requires_tool_execution && result.tool_calls.length > 0) {
        // Execute tools automatically
        for (const toolCall of result.tool_calls) {
          const toolResult = await executeTool.mutateAsync({
            tool_call: toolCall,
            conversation_history: result.conversation_history,
            provider: provider,
            model: provider === 'openai' ? openaiModel : anthropicModel,
            api_key: provider === 'openai' ? (openaiApiKey || undefined) : (anthropicApiKey || undefined),
            base_url: provider === 'openai' ? openaiBaseUrl : undefined,
            server_ids: selectedServerIds,
            authorization: authorization || undefined
          });

          // Update conversation history with tool results
          setConversationHistory(toolResult.conversation_history);

          // Add final response
          const finalMessage: Message = {
            role: 'assistant',
            content: toolResult.response,
            toolResults: [toolResult.tool_execution_result],
            usage: toolResult.usage
          };

          setMessages(prev => [...prev, finalMessage]);
        }
      }
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `Error: ${error?.response?.data?.detail || error.message || 'Failed to communicate with AI'}`
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (isLoadingServers) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto px-6 py-8">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
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
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-lg">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold tracking-tight">AI Sandbox</h1>
              <p className="text-muted-foreground">Test your deployed MCPs with AI Agent</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Server Selection Sidebar */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Select MCP Servers</CardTitle>
                <CardDescription>Choose one or more servers</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {/* Search Input */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    type="text"
                    placeholder="Search servers..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 text-sm"
                  />
                </div>

                {/* Selected Count */}
                {selectedServerIds.length > 0 && (
                  <div className="flex items-center justify-between px-2 py-1 bg-primary/10 rounded-lg">
                    <span className="text-xs font-medium">{selectedServerIds.length} selected</span>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setSelectedServerIds([])}
                      className="h-6 text-xs"
                    >
                      Clear
                    </Button>
                  </div>
                )}

                {/* Server List */}
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {servers.length === 0 ? (
                    <div className="text-center py-8">
                      <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                      <p className="text-sm text-muted-foreground">
                        {searchQuery ? `No servers match "${searchQuery}"` : 'No deployed MCP servers found'}
                      </p>
                    </div>
                  ) : (
                    servers.map((server: any) => (
                      <div
                        key={server.id}
                        className={`flex items-start gap-3 p-3 rounded-xl border-2 transition-all cursor-pointer ${
                          selectedServerIds.includes(server.id)
                            ? 'border-primary bg-primary/5'
                            : 'border-border hover:border-primary/50'
                        }`}
                        onClick={() => handleToggleServer(server.id)}
                      >
                        <Checkbox
                          checked={selectedServerIds.includes(server.id)}
                          onCheckedChange={() => handleToggleServer(server.id)}
                          className="mt-1"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-sm mb-1 truncate">{server.server_name}</div>
                          <div className="text-xs text-muted-foreground mb-2 truncate">
                            {server.project_name}
                          </div>
                          <Badge variant="secondary" className="text-xs">
                            {server.selected_endpoints_count} tools
                          </Badge>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Tools Info */}
            {selectedServerIds.length > 0 && (
              <Card className="mt-4">
                <CardHeader>
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Wrench className="w-4 h-4" />
                    Available Tools
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {selectedServers.map((server: any) => (
                      <div key={server.id} className="p-2 bg-secondary/50 rounded-lg">
                        <div className="text-xs font-semibold truncate">{server.server_name}</div>
                        <div className="text-xs text-muted-foreground">
                          {server.selected_endpoints_count} tool{server.selected_endpoints_count !== 1 ? 's' : ''}
                        </div>
                      </div>
                    ))}
                    <div className="pt-2 border-t">
                      <div className="text-sm font-semibold">
                        Total: {totalToolCount} tool{totalToolCount !== 1 ? 's' : ''}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* AI Provider Configuration */}
            <Card className="mt-4">
              <CardHeader>
                <div
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => setShowConfig(!showConfig)}
                >
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Settings className="w-4 h-4" />
                    AI Configuration
                  </CardTitle>
                  {showConfig ? (
                    <ChevronUp className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </div>
              </CardHeader>
              {showConfig && (
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="provider" className="text-xs">Provider</Label>
                    <Select
                      id="provider"
                      value={provider}
                      onChange={(e) => setProvider(e.target.value as 'anthropic' | 'openai')}
                    >
                      <option value="anthropic">Anthropic Claude</option>
                      <option value="openai">OpenAI Compatible</option>
                    </Select>
                  </div>

                  {provider === 'anthropic' ? (
                    <>
                      <div className="space-y-2">
                        <Label htmlFor="anthropic-model" className="text-xs">Model</Label>
                        <Input
                          id="anthropic-model"
                          value={anthropicModel}
                          onChange={(e) => setAnthropicModel(e.target.value)}
                          placeholder="claude-3-haiku-20240307"
                          className="text-sm"
                        />
                        <p className="text-xs text-muted-foreground">Leave empty to use backend default</p>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="anthropic-api-key" className="text-xs">API Key (Optional)</Label>
                        <Input
                          id="anthropic-api-key"
                          type="password"
                          value={anthropicApiKey}
                          onChange={(e) => setAnthropicApiKey(e.target.value)}
                          placeholder="sk-ant-..."
                          className="text-sm"
                        />
                        <p className="text-xs text-muted-foreground">Leave empty to use backend configuration</p>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="space-y-2">
                        <Label htmlFor="openai-model" className="text-xs">Model</Label>
                        <Input
                          id="openai-model"
                          value={openaiModel}
                          onChange={(e) => setOpenaiModel(e.target.value)}
                          placeholder="gpt-4o"
                          className="text-sm"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="openai-base-url" className="text-xs">Base URL</Label>
                        <Input
                          id="openai-base-url"
                          value={openaiBaseUrl}
                          onChange={(e) => setOpenaiBaseUrl(e.target.value)}
                          placeholder="https://api.openai.com/v1"
                          className="text-sm"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="openai-api-key" className="text-xs">API Key</Label>
                        <Input
                          id="openai-api-key"
                          type="password"
                          value={openaiApiKey}
                          onChange={(e) => setOpenaiApiKey(e.target.value)}
                          placeholder="sk-..."
                          className="text-sm"
                        />
                      </div>
                    </>
                  )}

                  <div className="space-y-2 pt-4 border-t">
                    <Label htmlFor="authorization" className="text-xs font-semibold">Authorization (Optional)</Label>
                    <Input
                      id="authorization"
                      type="password"
                      value={authorization}
                      onChange={(e) => setAuthorization(e.target.value)}
                      placeholder="Bearer your-token-here"
                      className="text-sm"
                    />
                    <p className="text-xs text-muted-foreground">
                      Authorization header for API calls. Auto-injected into all tool calls.
                    </p>
                  </div>

                  <div className="text-xs text-muted-foreground pt-2 border-t">
                    {provider === 'anthropic'
                      ? 'Anthropic Claude - Override backend defaults or leave empty'
                      : 'OpenAI-compatible API with custom configuration'}
                  </div>
                </CardContent>
              )}
            </Card>
          </div>

          {/* Chat Interface */}
          <div className="lg:col-span-3">
            {selectedServerIds.length === 0 ? (
              <Card className="h-[600px] flex items-center justify-center">
                <CardContent className="text-center">
                  <Sparkles className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-xl font-semibold mb-2">Ready to test!</h3>
                  <p className="text-muted-foreground">
                    Select one or more MCP servers from the left to start testing
                  </p>
                </CardContent>
              </Card>
            ) : (
              <Card className="h-[600px] flex flex-col">
                <CardHeader className="border-b">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <CardTitle className="truncate">
                        {selectedServers.length === 1
                          ? selectedServers[0].server_name
                          : `${selectedServers.length} MCP Servers`}
                      </CardTitle>
                      <CardDescription>
                        {selectedServers.length > 1 && (
                          <div className="text-xs mb-1">
                            {selectedServers.map((s: any) => s.server_name).join(', ')}
                          </div>
                        )}
                        Testing with {provider === 'anthropic' ? `Anthropic (${anthropicModel || 'claude-3-haiku-20240307'})` : `OpenAI (${openaiModel})`} - {totalToolCount} tools available
                      </CardDescription>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleClearChat}
                    >
                      Clear Chat
                    </Button>
                  </div>
                </CardHeader>

                {/* Messages */}
                <CardContent className="flex-1 overflow-y-auto p-6 space-y-4">
                  {messages.length === 0 ? (
                    <div className="h-full flex items-center justify-center text-center">
                      <div>
                        <Bot className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                        <p className="text-muted-foreground">
                          Start a conversation with AI Agent
                        </p>
                        <p className="text-sm text-muted-foreground mt-1">
                          AI Agent can use {totalToolCount} available tool{totalToolCount !== 1 ? 's' : ''} from {selectedServers.length} server{selectedServers.length !== 1 ? 's' : ''}
                        </p>
                      </div>
                    </div>
                  ) : (
                    messages.map((message, index) => (
                      <div
                        key={index}
                        className={`flex gap-3 ${
                          message.role === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        {message.role === 'assistant' && (
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center flex-shrink-0">
                            <Bot className="w-5 h-5 text-white" />
                          </div>
                        )}
                        <div
                          className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                            message.role === 'user'
                              ? 'bg-primary text-primary-foreground'
                              : 'bg-secondary'
                          }`}
                        >
                          <p className="whitespace-pre-wrap">{message.content}</p>
                          {message.toolCalls && message.toolCalls.length > 0 && (
                            <div className="mt-2 pt-2 border-t border-border/50">
                              <p className="text-xs font-semibold mb-1">Tool Calls:</p>
                              {message.toolCalls.map((tool, i) => (
                                <div key={i} className="text-xs bg-background/50 rounded p-2 mb-1">
                                  <span className="font-mono">{tool.name}</span>
                                  <pre className="text-xs mt-1 overflow-x-auto">
                                    {JSON.stringify(tool.input, null, 2)}
                                  </pre>
                                </div>
                              ))}
                            </div>
                          )}
                          {message.usage && (
                            <div className="mt-2 text-xs opacity-70">
                              Tokens: {message.usage.input_tokens} in / {message.usage.output_tokens} out
                            </div>
                          )}
                        </div>
                        {message.role === 'user' && (
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center flex-shrink-0">
                            <User className="w-5 h-5 text-white" />
                          </div>
                        )}
                      </div>
                    ))
                  )}
                  <div ref={messagesEndRef} />
                </CardContent>

                {/* Input */}
                <div className="border-t p-4">
                  <div className="flex gap-2">
                    <Input
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Type your message to AI Agent..."
                      disabled={testWithAI.isPending || executeTool.isPending}
                      className="flex-1"
                    />
                    <Button
                      onClick={handleSendMessage}
                      disabled={!inputMessage.trim() || testWithAI.isPending || executeTool.isPending}
                      className="rounded-full"
                    >
                      {testWithAI.isPending || executeTool.isPending ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Send className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                  {(testWithAI.isPending || executeTool.isPending) && (
                    <p className="text-xs text-muted-foreground mt-2">
                      {executeTool.isPending ? 'Executing tools...' : 'Thinking...'}
                    </p>
                  )}
                </div>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default AITestingPage;
