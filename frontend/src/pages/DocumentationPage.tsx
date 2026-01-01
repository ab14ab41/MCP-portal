import { BookOpen, Rocket, Zap, Settings, TestTube, Code, HelpCircle, ExternalLink } from 'lucide-react';
import { useState } from 'react';
import Header from '@/components/layout/Header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

function DocumentationPage() {
  const [activeSection, setActiveSection] = useState('overview');

  const sections = [
    { id: 'overview', name: 'Overview', icon: BookOpen },
    { id: 'getting-started', name: 'Getting Started', icon: Rocket },
    { id: 'features', name: 'Features', icon: Zap },
    { id: 'workflow', name: 'Workflow', icon: Settings },
    { id: 'ai-sandbox', name: 'AI Sandbox', icon: TestTube },
    { id: 'api-reference', name: 'API Reference', icon: Code },
    { id: 'troubleshooting', name: 'Troubleshooting', icon: HelpCircle },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-6 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold tracking-tight">Documentation</h1>
              <p className="text-muted-foreground">Complete guide to MCP Portal</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <Card className="sticky top-20">
              <CardHeader>
                <CardTitle className="text-base">Contents</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1">
                {sections.map((section) => {
                  const Icon = section.icon;
                  return (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                        activeSection === section.id
                          ? 'bg-primary text-primary-foreground'
                          : 'hover:bg-secondary text-muted-foreground hover:text-foreground'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      {section.name}
                    </button>
                  );
                })}
              </CardContent>
            </Card>
          </div>

          {/* Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Overview */}
            {activeSection === 'overview' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>What is MCP Portal?</CardTitle>
                    <CardDescription>
                      Transform REST APIs into AI-usable tools
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-muted-foreground">
                      MCP Portal is a web application that automatically converts Swagger/OpenAPI specifications
                      into deployable MCP (Model Context Protocol) servers. It enables AI assistants like Claude
                      to interact with any REST API through a standardized tool interface.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                      <div className="border rounded-lg p-4">
                        <h4 className="font-semibold mb-2">🎯 Purpose</h4>
                        <p className="text-sm text-muted-foreground">
                          Bridge the gap between REST APIs and AI agents without manual coding
                        </p>
                      </div>
                      <div className="border rounded-lg p-4">
                        <h4 className="font-semibold mb-2">⚡ Benefits</h4>
                        <p className="text-sm text-muted-foreground">
                          Automated conversion, customizable tools, instant AI testing
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Key Concepts</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <h4 className="font-semibold mb-1">Projects</h4>
                      <p className="text-sm text-muted-foreground">
                        Organizational containers for related MCP servers and API specifications
                      </p>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">Swagger/OpenAPI Specifications</h4>
                      <p className="text-sm text-muted-foreground">
                        REST API definitions that describe endpoints, parameters, and responses
                      </p>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">MCP Servers</h4>
                      <p className="text-sm text-muted-foreground">
                        Generated Python servers that expose API endpoints as AI-usable tools
                      </p>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">AI Sandbox</h4>
                      <p className="text-sm text-muted-foreground">
                        Testing environment where you can interact with deployed MCP servers using AI models
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>External Documentation</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button
                      variant="outline"
                      className="w-full justify-between"
                      onClick={() => window.open('https://github.com/yourusername/mcp-portal/blob/main/DOCUMENTATION.md', '_blank')}
                    >
                      <span className="flex items-center gap-2">
                        <BookOpen className="w-4 h-4" />
                        Complete Documentation
                      </span>
                      <ExternalLink className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full justify-between"
                      onClick={() => window.open('https://github.com/yourusername/mcp-portal/blob/main/AI_TESTING_SETUP.md', '_blank')}
                    >
                      <span className="flex items-center gap-2">
                        <TestTube className="w-4 h-4" />
                        AI Sandbox Guide
                      </span>
                      <ExternalLink className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full justify-between"
                      onClick={() => window.open('http://localhost:8000/docs', '_blank')}
                    >
                      <span className="flex items-center gap-2">
                        <Code className="w-4 h-4" />
                        API Documentation (Swagger)
                      </span>
                      <ExternalLink className="w-4 h-4" />
                    </Button>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Getting Started */}
            {activeSection === 'getting-started' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Quick Start</CardTitle>
                    <CardDescription>Get up and running in minutes</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-6">
                      <div className="flex gap-4">
                        <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center flex-shrink-0 font-semibold">
                          1
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold mb-2">Prerequisites</h4>
                          <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                            <li>Docker and Docker Compose installed</li>
                            <li>Anthropic API key (for AI testing)</li>
                            <li>(Optional) OpenAI API key</li>
                          </ul>
                        </div>
                      </div>

                      <div className="flex gap-4">
                        <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center flex-shrink-0 font-semibold">
                          2
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold mb-2">Configure Environment</h4>
                          <pre className="bg-secondary rounded-lg p-4 text-xs overflow-x-auto">
{`# Edit backend/.env
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx  # Optional`}
                          </pre>
                        </div>
                      </div>

                      <div className="flex gap-4">
                        <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center flex-shrink-0 font-semibold">
                          3
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold mb-2">Start Services</h4>
                          <pre className="bg-secondary rounded-lg p-4 text-xs">
{`docker-compose up -d`}
                          </pre>
                          <p className="text-sm text-muted-foreground mt-2">
                            Access the app at <code className="bg-secondary px-2 py-1 rounded">http://localhost:5173</code>
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>First Project</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ol className="space-y-4 text-sm">
                      <li className="flex gap-3">
                        <Badge variant="secondary">1</Badge>
                        <div>
                          <strong>Create a Project:</strong> Go to Projects page and click "New Project"
                        </div>
                      </li>
                      <li className="flex gap-3">
                        <Badge variant="secondary">2</Badge>
                        <div>
                          <strong>Import API Spec:</strong> Upload a Swagger/OpenAPI file or fetch from URL
                        </div>
                      </li>
                      <li className="flex gap-3">
                        <Badge variant="secondary">3</Badge>
                        <div>
                          <strong>Configure Endpoints:</strong> Select endpoints and add descriptions
                        </div>
                      </li>
                      <li className="flex gap-3">
                        <Badge variant="secondary">4</Badge>
                        <div>
                          <strong>Generate MCP:</strong> Click "Generate MCP" to create your server
                        </div>
                      </li>
                      <li className="flex gap-3">
                        <Badge variant="secondary">5</Badge>
                        <div>
                          <strong>Deploy & Test:</strong> Deploy the server and test in AI Sandbox
                        </div>
                      </li>
                    </ol>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Features */}
            {activeSection === 'features' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Core Features</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="border rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
                            📥
                          </div>
                          <h4 className="font-semibold">Flexible Import</h4>
                        </div>
                        <ul className="text-sm text-muted-foreground space-y-1">
                          <li>• Upload files (JSON/YAML)</li>
                          <li>• Fetch from URL</li>
                          <li>• Paste content</li>
                          <li>• Connect to API endpoint</li>
                        </ul>
                      </div>

                      <div className="border rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center">
                            ⚙️
                          </div>
                          <h4 className="font-semibold">Advanced Config</h4>
                        </div>
                        <ul className="text-sm text-muted-foreground space-y-1">
                          <li>• Select endpoints</li>
                          <li>• Override parameter requirements</li>
                          <li>• Custom descriptions</li>
                          <li>• Base URL management</li>
                        </ul>
                      </div>

                      <div className="border rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center">
                            🤖
                          </div>
                          <h4 className="font-semibold">AI Sandbox</h4>
                        </div>
                        <ul className="text-sm text-muted-foreground space-y-1">
                          <li>• Anthropic Claude</li>
                          <li>• OpenAI & compatible</li>
                          <li>• Multi-MCP testing</li>
                          <li>• Real-time chat</li>
                        </ul>
                      </div>

                      <div className="border rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="w-8 h-8 rounded-lg bg-orange-500/10 flex items-center justify-center">
                            🚀
                          </div>
                          <h4 className="font-semibold">Deployment</h4>
                        </div>
                        <ul className="text-sm text-muted-foreground space-y-1">
                          <li>• One-click deploy</li>
                          <li>• Server management</li>
                          <li>• Real-time status</li>
                          <li>• Search & filter</li>
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Parameter Override Feature</CardTitle>
                    <CardDescription>Customize which parameters are required</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <p className="text-sm text-muted-foreground">
                      Override the original API specification's parameter requirements to better suit AI usage:
                    </p>
                    <div className="border-l-4 border-green-500 bg-green-500/10 p-4 rounded">
                      <p className="text-sm">
                        <strong>Make optional parameters mandatory:</strong> Prevent errors from missing critical parameters
                      </p>
                    </div>
                    <div className="border-l-4 border-blue-500 bg-blue-500/10 p-4 rounded">
                      <p className="text-sm">
                        <strong>Make required parameters optional:</strong> Allow AI to use default values when appropriate
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Workflow */}
            {activeSection === 'workflow' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Complete Workflow</CardTitle>
                    <CardDescription>Step-by-step process from API to AI</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-6">
                      {[
                        {
                          step: 1,
                          title: 'Create Project',
                          description: 'Organize your MCP servers by creating a project',
                          details: ['Navigate to Projects page', 'Click "New Project"', 'Enter name and description']
                        },
                        {
                          step: 2,
                          title: 'Import Swagger Spec',
                          description: 'Bring in your API specification',
                          details: [
                            'Upload JSON/YAML file',
                            'Or fetch from URL',
                            'Or paste content directly',
                            'System parses and validates'
                          ]
                        },
                        {
                          step: 3,
                          title: 'Configure Endpoints',
                          description: 'Customize which endpoints become AI tools',
                          details: [
                            'Select endpoints to expose',
                            'Add AI-friendly descriptions',
                            'Override parameter requirements',
                            'Review request/response schemas'
                          ]
                        },
                        {
                          step: 4,
                          title: 'Generate MCP Server',
                          description: 'Create Python MCP server code',
                          details: [
                            'Click "Generate MCP"',
                            'Preview generated code',
                            'Download or deploy',
                            'Server ready in seconds'
                          ]
                        },
                        {
                          step: 5,
                          title: 'Deploy & Manage',
                          description: 'Make your MCP server accessible',
                          details: [
                            'One-click deployment',
                            'HTTP-streamable endpoint',
                            'Start/stop/restart controls',
                            'Monitor server status'
                          ]
                        },
                        {
                          step: 6,
                          title: 'Test with AI',
                          description: 'Validate functionality in AI Sandbox',
                          details: [
                            'Select deployed server(s)',
                            'Choose AI provider',
                            'Chat and test tools',
                            'Monitor token usage'
                          ]
                        }
                      ].map((item) => (
                        <div key={item.step} className="flex gap-4">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-blue-600 text-white flex items-center justify-center flex-shrink-0 font-bold shadow-lg">
                            {item.step}
                          </div>
                          <div className="flex-1">
                            <h4 className="font-semibold mb-1">{item.title}</h4>
                            <p className="text-sm text-muted-foreground mb-2">{item.description}</p>
                            <ul className="text-xs text-muted-foreground space-y-1">
                              {item.details.map((detail, idx) => (
                                <li key={idx}>→ {detail}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* AI Sandbox */}
            {activeSection === 'ai-sandbox' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>AI Sandbox Overview</CardTitle>
                    <CardDescription>Test your MCP servers with AI models</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-muted-foreground">
                      The AI Sandbox provides an interactive environment to test your deployed MCP servers
                      with multiple AI providers and models.
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Supported AI Providers</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold">Anthropic Claude</h4>
                          <Badge>Recommended</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">
                          Excellent at complex workflows and tool usage
                        </p>
                        <div className="flex flex-wrap gap-2">
                          <Badge variant="outline">claude-3-opus-20240229</Badge>
                          <Badge variant="outline">claude-3-5-sonnet-20241022</Badge>
                          <Badge variant="outline">claude-3-haiku-20240307</Badge>
                        </div>
                      </div>

                      <div className="border rounded-lg p-4">
                        <h4 className="font-semibold mb-2">OpenAI & Compatible</h4>
                        <p className="text-sm text-muted-foreground mb-3">
                          Supports OpenAI, Azure OpenAI, and local models
                        </p>
                        <div className="flex flex-wrap gap-2">
                          <Badge variant="outline">gpt-4o</Badge>
                          <Badge variant="outline">gpt-4-turbo</Badge>
                          <Badge variant="outline">gpt-3.5-turbo</Badge>
                          <Badge variant="outline">Local (Ollama)</Badge>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Multi-MCP Testing</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <p className="text-sm text-muted-foreground">
                      Select multiple MCP servers to combine their tools in a single AI session.
                    </p>
                    <div className="bg-secondary rounded-lg p-4">
                      <p className="text-sm font-medium mb-2">Example: Cross-API Workflow</p>
                      <pre className="text-xs">
{`Selected MCPs:
✓ GitHub API (12 tools)
✓ Slack API (8 tools)

Query: "When a new issue is created,
       notify #dev channel"

AI will:
1. Check GitHub for new issues
2. Send Slack message to #dev`}
                      </pre>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Configuration Options</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3 text-sm">
                      <div>
                        <strong>API Key Override:</strong>
                        <p className="text-muted-foreground">Use different API keys per session without changing backend config</p>
                      </div>
                      <div>
                        <strong>Model Selection:</strong>
                        <p className="text-muted-foreground">Choose specific models or use custom model names</p>
                      </div>
                      <div>
                        <strong>Base URL (OpenAI):</strong>
                        <p className="text-muted-foreground">Point to Azure, local models, or compatible APIs</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* API Reference */}
            {activeSection === 'api-reference' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>API Documentation</CardTitle>
                    <CardDescription>RESTful API endpoints</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-muted-foreground">
                      MCP Portal provides a comprehensive REST API for all operations.
                    </p>
                    <Button
                      variant="default"
                      className="w-full"
                      onClick={() => window.open('http://localhost:8000/docs', '_blank')}
                    >
                      <Code className="w-4 h-4 mr-2" />
                      View Interactive API Docs (Swagger UI)
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Main Endpoints</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {[
                        { method: 'POST', path: '/api/v1/projects', desc: 'Create project' },
                        { method: 'GET', path: '/api/v1/projects', desc: 'List projects' },
                        { method: 'POST', path: '/api/v1/projects/{id}/swagger-specs/upload', desc: 'Upload spec' },
                        { method: 'POST', path: '/api/v1/swagger-specs/{id}/generate-mcp', desc: 'Generate MCP' },
                        { method: 'POST', path: '/api/v1/swagger-specs/generated-servers/{id}/deploy', desc: 'Deploy server' },
                        { method: 'GET', path: '/api/v1/swagger-specs/deployed-servers', desc: 'List deployments' },
                        { method: 'POST', path: '/api/v1/ai-testing/deployed-servers/{id}/test', desc: 'Test with AI' },
                      ].map((endpoint) => (
                        <div key={endpoint.path} className="flex items-start gap-3 p-3 border rounded-lg">
                          <Badge variant={endpoint.method === 'GET' ? 'secondary' : 'default'} className="mt-0.5">
                            {endpoint.method}
                          </Badge>
                          <div className="flex-1 min-w-0">
                            <code className="text-xs break-all">{endpoint.path}</code>
                            <p className="text-xs text-muted-foreground mt-1">{endpoint.desc}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Troubleshooting */}
            {activeSection === 'troubleshooting' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Common Issues</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {[
                      {
                        issue: 'Can\'t connect to localhost API from Docker',
                        solution: 'Use host.docker.internal instead of localhost',
                        example: 'http://host.docker.internal:8000/openapi.json'
                      },
                      {
                        issue: 'Anthropic API errors in AI Sandbox',
                        solution: 'Ensure ANTHROPIC_API_KEY is set in backend/.env and restart backend',
                        example: 'docker-compose restart backend'
                      },
                      {
                        issue: 'MCP server shows inactive after deployment',
                        solution: 'Check Docker logs and verify base URL is accessible',
                        example: 'docker-compose logs backend'
                      },
                      {
                        issue: 'Frontend shows blank screen',
                        solution: 'Verify backend is running and check browser console',
                        example: 'curl http://localhost:8000/health'
                      },
                    ].map((item, idx) => (
                      <div key={idx} className="border rounded-lg p-4">
                        <h4 className="font-semibold mb-2 text-red-600 dark:text-red-400">
                          ❌ {item.issue}
                        </h4>
                        <p className="text-sm text-muted-foreground mb-2">
                          <strong className="text-green-600 dark:text-green-400">✓ Solution:</strong> {item.solution}
                        </p>
                        {item.example && (
                          <pre className="bg-secondary rounded p-2 text-xs mt-2 overflow-x-auto">
                            {item.example}
                          </pre>
                        )}
                      </div>
                    ))}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Debug Commands</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <p className="text-sm font-medium mb-1">View all logs:</p>
                        <pre className="bg-secondary rounded p-3 text-xs">docker-compose logs -f</pre>
                      </div>
                      <div>
                        <p className="text-sm font-medium mb-1">Check backend health:</p>
                        <pre className="bg-secondary rounded p-3 text-xs">curl http://localhost:8000/health</pre>
                      </div>
                      <div>
                        <p className="text-sm font-medium mb-1">Restart services:</p>
                        <pre className="bg-secondary rounded p-3 text-xs">docker-compose restart</pre>
                      </div>
                      <div>
                        <p className="text-sm font-medium mb-1">Reset database:</p>
                        <pre className="bg-secondary rounded p-3 text-xs">docker-compose down -v && docker-compose up -d</pre>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Get Help</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button
                      variant="outline"
                      className="w-full justify-between"
                      onClick={() => window.open('https://github.com/yourusername/mcp-portal/issues', '_blank')}
                    >
                      <span>Report an Issue</span>
                      <ExternalLink className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full justify-between"
                      onClick={() => window.open('https://github.com/yourusername/mcp-portal/discussions', '_blank')}
                    >
                      <span>Join Discussions</span>
                      <ExternalLink className="w-4 h-4" />
                    </Button>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default DocumentationPage;
