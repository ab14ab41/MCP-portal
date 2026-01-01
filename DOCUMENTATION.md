# MCP Portal - Complete Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Core Concepts](#core-concepts)
4. [User Guide](#user-guide)
5. [AI Sandbox](#ai-sandbox)
6. [API Reference](#api-reference)
7. [Configuration](#configuration)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Topics](#advanced-topics)

---

## Introduction

MCP Portal is a web application that transforms REST APIs into AI-usable tools by converting Swagger/OpenAPI specifications into deployable MCP (Model Context Protocol) servers. It provides a complete workflow from API specification to AI-powered testing.

### What is MCP?

Model Context Protocol (MCP) is a standardized protocol developed by Anthropic for connecting AI assistants with external tools and data sources. MCP servers expose tools that AI models like Claude can discover and use automatically.

### Why MCP Portal?

- **Automated Conversion**: Turn any REST API into MCP tools without manual coding
- **Customizable**: Select which endpoints to expose and customize descriptions
- **AI Testing**: Test your MCP servers with Claude or OpenAI models instantly
- **Production Ready**: Deploy MCP servers as HTTP-streamable endpoints
- **Multi-API Support**: Combine multiple APIs in a single AI session

---

## Getting Started

### Prerequisites

- **Docker** and **Docker Compose** installed
- (Optional) **Node.js 20+** for local frontend development
- (Optional) **Python 3.11+** for local backend development
- **Anthropic API Key** (for Claude AI testing)
- (Optional) **OpenAI API Key** (for OpenAI model testing)

### Quick Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mcp-portal.git
   cd mcp-portal
   ```

2. **Configure environment**
   ```bash
   cp backend/.env.example backend/.env
   ```

   Edit `backend/.env`:
   ```env
   # Required for AI Sandbox
   ANTHROPIC_API_KEY=sk-ant-xxxxx

   # Optional for AI Sandbox
   OPENAI_API_KEY=sk-xxxxx
   OPENAI_BASE_URL=https://api.openai.com/v1
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### First Steps

1. Create your first project
2. Import a Swagger/OpenAPI specification
3. Configure endpoints and parameters
4. Generate and deploy your MCP server
5. Test with AI in the AI Sandbox

---

## Core Concepts

### Projects

Projects are organizational containers for related MCP servers. Each project can contain multiple Swagger specifications and their generated MCP servers.

**Use Cases:**
- Organize APIs by application or service
- Group related microservices
- Separate development environments

### Swagger Specifications

OpenAPI (formerly Swagger) specifications define REST APIs. MCP Portal supports:
- **OpenAPI 2.0** (Swagger)
- **OpenAPI 3.0+**
- JSON and YAML formats

### Endpoint Configurations

Each API endpoint can be individually configured:
- **Selection**: Choose which endpoints to expose as MCP tools
- **Tool Names**: Customize the MCP tool name
- **Descriptions**: Add AI-friendly descriptions
- **Parameter Overrides**: Make required parameters optional or vice versa

### Parameter Mandatory Override

A key feature that allows customizing which parameters are required:

**Original Spec:**
```json
{
  "name": "limit",
  "type": "integer",
  "required": false
}
```

**User Override:**
- Check "Make this parameter mandatory"
- Generated MCP tool will require this parameter

**Use Cases:**
- Prevent errors from missing critical parameters
- Simplify API usage by making rarely-used parameters optional
- Enforce best practices for AI tool usage

### Generated MCP Servers

Python-based MCP servers created from your configurations:
- Uses FastMCP framework
- Includes all selected endpoints as tools
- Contains proper error handling
- Ready to deploy and use

### Deployment

MCP servers can be deployed as HTTP-streamable endpoints:
- One-click deployment
- Real-time status monitoring
- Start, stop, restart capabilities
- Accessible via MCP protocol

---

## User Guide

### 1. Creating a Project

**Steps:**
1. Click "New Project" on the Projects page
2. Enter project name and description
3. Click "Create Project"

**Tips:**
- Use descriptive names (e.g., "GitHub API", "Stripe Payment Gateway")
- Add detailed descriptions for team collaboration

### 2. Importing API Specifications

MCP Portal supports four import methods:

#### Method 1: File Upload

**Supported Formats:**
- `.json` files
- `.yaml` or `.yml` files
- Up to 10MB file size

**Steps:**
1. Navigate to your project
2. Click "Import Swagger Spec"
3. Select "Upload File" tab
4. Drag and drop or click to select file
5. Click "Parse Specification"

#### Method 2: Fetch from URL

**Supported URLs:**
- Public HTTP/HTTPS endpoints
- OpenAPI spec URLs (e.g., `https://api.example.com/openapi.json`)

**Docker Networking:**
When testing with local APIs running in Docker:
```
❌ Wrong: http://localhost:8000/openapi.json
✅ Correct: http://host.docker.internal:8000/openapi.json
```

**Steps:**
1. Click "Fetch from URL" tab
2. Enter the URL
3. Click "Fetch & Parse"

#### Method 3: Paste Content

**Use Cases:**
- Copy spec from documentation
- Quick testing with spec snippets
- Sharing specs without file transfer

**Steps:**
1. Click "Paste Content" tab
2. Paste your JSON or YAML spec
3. Click "Parse Specification"

#### Method 4: Connect to API

**Use Cases:**
- Discover API specs automatically
- Connect to live API endpoints

**Steps:**
1. Click "Connect to API" tab
2. Enter the base API URL
3. System attempts to find OpenAPI spec
4. Click "Parse" when found

### 3. Configuring Endpoints

After importing, configure which endpoints to expose:

#### Selecting Endpoints

**Bulk Actions:**
- "Select All" - Enable all endpoints
- "Deselect All" - Disable all endpoints
- Individual checkboxes for fine control

**Filtering:**
- Search by path or method
- Filter by HTTP method (GET, POST, PUT, DELETE, PATCH)

#### Customizing Endpoints

For each selected endpoint:

**1. Tool Name**
- Auto-generated from method and path
- Can be customized (e.g., `get_user_profile`)
- Must be valid Python function name

**2. Description** (Required)
- Explain what the tool does
- Include examples of when to use it
- AI-friendly language

Example:
```
❌ Bad: "Gets user"
✅ Good: "Retrieve detailed user profile information including email, name, and preferences by user ID"
```

**3. Parameter Configuration**

For each parameter:

**Parameter Metadata:**
- Name (from spec)
- Type (string, integer, boolean, etc.)
- Location (path, query, header, body)
- Original required status (from spec)

**User Configuration:**
- **Mandatory Toggle**: Override original required status
- **Description**: Add AI-friendly parameter description

**Example Configuration:**

```
Parameter: user_id
Type: integer
Location: path
Spec Required: ✓ Yes

☐ Make this parameter mandatory
[Already required in spec]

Description:
┌──────────────────────────────────────────┐
│ The unique identifier of the user to     │
│ retrieve. Must be a positive integer.    │
└──────────────────────────────────────────┘
```

```
Parameter: include_deleted
Type: boolean
Location: query
Spec Required: ✗ No

☑ Make this parameter mandatory
[Override: Make required]

Description:
┌──────────────────────────────────────────┐
│ Whether to include deleted users in      │
│ results. Always set to true or false.    │
└──────────────────────────────────────────┘
```

### 4. Generating MCP Servers

Once endpoints are configured:

**Steps:**
1. Click "Generate MCP" button
2. Review server configuration:
   - Server name
   - Description
   - Selected endpoints count
3. Click "Generate"
4. Wait for generation (usually < 10 seconds)
5. Preview generated code

**Generated Files:**
- `server.py` - Main MCP server code
- `requirements.txt` - Python dependencies
- `README.md` - Usage instructions
- `config.example.json` - Configuration template

### 5. Deploying MCP Servers

**Deployment Options:**

#### Option 1: Deploy in MCP Portal
1. Click "Deploy" button after generation
2. Server becomes available at `/api/v1/mcp/serve/{server_id}`
3. Manage from Deployment page (start, stop, restart)

#### Option 2: Download and Run Locally
1. Click "Download" to get ZIP package
2. Extract files
3. Install dependencies: `pip install -r requirements.txt`
4. Run server: `python server.py`

### 6. Managing Deployments

Navigate to the **Deployment** page to manage active servers.

**Server Information:**
- Project name
- Server name
- Active/Inactive status
- Endpoint count
- Base URL (API being proxied)
- MCP Endpoint URL
- Deployment timestamp

**Actions:**

**Start** - Activate an inactive server
**Stop** - Deactivate without deleting
**Restart** - Stop and start (useful after base URL updates)
**Delete** - Permanently remove server
**View Info** - See available tools and schemas
**Copy Endpoint** - Copy MCP URL to clipboard

**Search:**
- Filter by project name
- Filter by server name
- Filter by base URL

---

## AI Sandbox

The AI Sandbox allows you to test deployed MCP servers with AI models.

### Supported AI Providers

#### 1. Anthropic Claude

**Models:**
- `claude-3-opus-20240229` (Most capable)
- `claude-3-5-sonnet-20241022` (Balanced)
- `claude-3-haiku-20240307` (Fast and cost-effective)

**Configuration:**
- API Key: Override backend default or use configured key
- Model: Select or enter custom model name

#### 2. OpenAI-Compatible APIs

**Supported Services:**
- OpenAI (GPT-4, GPT-4 Turbo, GPT-3.5)
- Azure OpenAI
- Local models (Ollama, LM Studio, etc.)
- Any OpenAI-compatible API

**Configuration:**
- API Key: Your OpenAI or compatible API key
- Base URL: API endpoint (default: `https://api.openai.com/v1`)
- Model: Model name (e.g., `gpt-4o`, `gpt-4-turbo`)

### Using AI Sandbox

#### 1. Select MCP Servers

**Single Server:**
- Click on one server in the sidebar
- AI will have access to that server's tools

**Multiple Servers:**
- Check multiple servers
- AI can use tools from all selected servers
- Useful for cross-API workflows

Example:
```
✓ GitHub API (12 tools)
✓ Slack API (8 tools)
✓ Stripe API (15 tools)

Total: 35 tools available
```

#### 2. Configure AI Provider

**For Anthropic Claude:**
```
Provider: Anthropic Claude
Model: claude-3-5-sonnet-20241022
API Key: [Optional override]
```

**For OpenAI:**
```
Provider: OpenAI
Model: gpt-4o
API Key: sk-proj-xxxxx
Base URL: https://api.openai.com/v1
```

**For Local Models:**
```
Provider: OpenAI
Model: llama2
API Key: not-needed
Base URL: http://localhost:11434/v1
```

#### 3. Start Chatting

**Example Interactions:**

**Simple Query:**
```
You: "Get the user with ID 123"
AI: [Calls get_user tool with user_id=123]
AI: "Here's the user information: John Doe, email: john@example.com, ..."
```

**Multi-Tool Workflow:**
```
You: "List all repositories for user 'octocat' and show me the latest commit for each"
AI: [Calls list_user_repos with username="octocat"]
AI: [Calls get_latest_commit for each repo]
AI: "I found 5 repositories. Here are the latest commits: ..."
```

**Cross-API Workflow:**
```
You: "When a new GitHub issue is created, send a message to #engineering on Slack"
AI: [Calls list_github_issues]
AI: [Calls send_slack_message to #engineering channel]
AI: "I've notified the #engineering channel about the 3 new issues..."
```

#### 4. Tool Execution Flow

1. **User sends message**
2. **AI analyzes** available tools and decides which to use
3. **Tool calls displayed** with parameters
4. **Automatic execution** against deployed MCP servers
5. **Results shown** with API responses
6. **AI processes** results and responds
7. **Conversation continues** with full context

#### 5. Monitoring

**Tool Call Visualization:**
```
🔧 Tool Call: get_user_profile
Parameters:
  user_id: 123
  include_preferences: true

✅ Result: Success (245ms)
```

**Token Usage:**
- Input tokens: Count of tokens sent to AI
- Output tokens: Count of tokens generated
- Tracks per-message and cumulative usage

### AI Sandbox Features

**Conversation History:**
- Full context maintained
- Scroll through past messages
- Tool calls preserved

**Tool Discovery:**
- View all available tools
- See tool descriptions
- Inspect input schemas

**Error Handling:**
- API errors displayed clearly
- Retry failed tool calls
- Helpful error messages

**Multi-Session:**
- Test different server combinations
- Compare AI provider responses
- Parallel testing workflows

---

## API Reference

### Base URL

```
http://localhost:8000/api/v1
```

### Authentication

Currently no authentication required (to be added in future versions).

### Projects API

#### Create Project
```http
POST /projects
Content-Type: application/json

{
  "name": "My Project",
  "description": "Project description"
}

Response: 201 Created
{
  "id": "uuid",
  "name": "My Project",
  "description": "Project description",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

#### List Projects
```http
GET /projects?search=keyword

Response: 200 OK
{
  "projects": [
    {
      "id": "uuid",
      "name": "My Project",
      "description": "...",
      "swagger_specs_count": 2,
      "generated_servers_count": 3,
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "total": 1
}
```

#### Get Project
```http
GET /projects/{project_id}

Response: 200 OK
{
  "id": "uuid",
  "name": "My Project",
  "description": "...",
  "swagger_specs": [...],
  "generated_servers": [...],
  "created_at": "...",
  "updated_at": "..."
}
```

#### Update Project
```http
PUT /projects/{project_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description"
}

Response: 200 OK
```

#### Delete Project
```http
DELETE /projects/{project_id}

Response: 204 No Content
```

### Swagger Specs API

#### Upload File
```http
POST /projects/{project_id}/swagger-specs/upload
Content-Type: multipart/form-data

file: <file>

Response: 201 Created
{
  "id": "uuid",
  "project_id": "uuid",
  "spec_version": "3.0.0",
  "title": "My API",
  "base_url": "https://api.example.com",
  "total_endpoints": 25,
  "endpoints_summary": {...}
}
```

#### Fetch from URL
```http
POST /projects/{project_id}/swagger-specs/from-url
Content-Type: application/json

{
  "url": "https://api.example.com/openapi.json"
}

Response: 201 Created
```

#### Paste Content
```http
POST /projects/{project_id}/swagger-specs/from-content
Content-Type: application/json

{
  "content": "openapi: 3.0.0\ninfo:\n  title: My API\n...",
  "format": "yaml"
}

Response: 201 Created
```

#### Update Base URL
```http
PATCH /swagger-specs/{spec_id}/base-url
Content-Type: application/json

{
  "base_url": "https://new-api.example.com"
}

Response: 200 OK
```

### Endpoint Configuration API

#### List Configurations
```http
GET /swagger-specs/{spec_id}/endpoint-configurations

Response: 200 OK
{
  "configurations": [
    {
      "id": "uuid",
      "swagger_spec_id": "uuid",
      "http_method": "GET",
      "path": "/users/{user_id}",
      "operation_id": "getUser",
      "is_selected": true,
      "mcp_tool_name": "get_user",
      "mcp_description": "Retrieve user by ID",
      "parameter_configurations": {
        "parameters": [
          {
            "name": "user_id",
            "type": "integer",
            "required": true,
            "user_required": true,
            "description": "User identifier",
            "location": "path"
          }
        ]
      }
    }
  ]
}
```

#### Batch Update
```http
POST /swagger-specs/{spec_id}/endpoint-configurations/batch
Content-Type: application/json

{
  "configurations": [
    {
      "id": "uuid",
      "is_selected": true,
      "mcp_tool_name": "get_user",
      "mcp_description": "Retrieve user profile...",
      "parameter_configurations": {
        "parameters": [...]
      }
    }
  ]
}

Response: 200 OK
```

### MCP Generation API

#### Generate Server
```http
POST /swagger-specs/{spec_id}/generate-mcp
Content-Type: application/json

{
  "server_name": "My API Server",
  "server_description": "MCP server for My API"
}

Response: 201 Created
{
  "id": "uuid",
  "server_name": "My API Server",
  "python_code": "from mcp.server.fastmcp import FastMCP\n...",
  "requirements_txt": "mcp[cli]>=1.2.0\nhttpx>=0.26.0\n...",
  "selected_endpoints_count": 10,
  "lines_of_code": 350,
  "generation_status": "completed"
}
```

#### Deploy Server
```http
POST /swagger-specs/generated-servers/{server_id}/deploy

Response: 200 OK
{
  "message": "MCP server deployed successfully",
  "deployment_url": "/api/v1/mcp/serve/{server_id}"
}
```

#### Undeploy Server
```http
POST /swagger-specs/generated-servers/{server_id}/undeploy

Response: 200 OK
{
  "message": "MCP server stopped"
}
```

#### List Deployed Servers
```http
GET /swagger-specs/deployed-servers?search=keyword

Response: 200 OK
{
  "servers": [
    {
      "id": "uuid",
      "server_name": "My API Server",
      "project_id": "uuid",
      "project_name": "My Project",
      "is_active": true,
      "base_url": "https://api.example.com",
      "deployment_url": "/api/v1/mcp/serve/uuid",
      "selected_endpoints_count": 10,
      "deployed_at": "..."
    }
  ]
}
```

### AI Testing API

#### Get Server Tools
```http
GET /ai-testing/deployed-servers/{server_id}/tools

Response: 200 OK
{
  "server_id": "uuid",
  "server_name": "My API Server",
  "tools": [
    {
      "name": "get_user",
      "description": "Retrieve user profile information",
      "input_schema": {
        "type": "object",
        "properties": {
          "user_id": {
            "type": "integer",
            "description": "User identifier"
          }
        },
        "required": ["user_id"]
      }
    }
  ],
  "tool_count": 10
}
```

#### Test with AI
```http
POST /ai-testing/deployed-servers/{server_id}/test
Content-Type: application/json

{
  "message": "Get user with ID 123",
  "conversation_history": [],
  "provider": "anthropic",
  "model": "claude-3-5-sonnet-20241022",
  "api_key": "sk-ant-xxxxx",
  "server_ids": ["uuid1", "uuid2"]
}

Response: 200 OK
{
  "response": "Here's the user information...",
  "tool_calls": [
    {
      "id": "call_123",
      "name": "get_user",
      "input": {
        "user_id": 123
      }
    }
  ],
  "conversation_history": [...],
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 150,
    "output_tokens": 80
  },
  "requires_tool_execution": true
}
```

#### Execute Tool
```http
POST /ai-testing/deployed-servers/{server_id}/execute-tool
Content-Type: application/json

{
  "tool_call": {
    "id": "call_123",
    "name": "get_user",
    "input": {
      "user_id": 123
    }
  },
  "conversation_history": [...],
  "provider": "anthropic",
  "server_ids": ["uuid1", "uuid2"]
}

Response: 200 OK
{
  "response": "The user information shows...",
  "tool_execution_result": {
    "user_id": 123,
    "name": "John Doe",
    "email": "john@example.com"
  },
  "additional_tool_calls": [],
  "conversation_history": [...],
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 200,
    "output_tokens": 100
  }
}
```

### MCP Serving API

#### MCP SSE Endpoint
```http
GET /mcp/serve/{server_id}

Server-Sent Events stream for MCP protocol communication
```

#### MCP Info
```http
GET /mcp/serve/{server_id}/info

Response: 200 OK
{
  "server_id": "uuid",
  "base_url": "https://api.example.com",
  "registered_at": "...",
  "tools_count": 10,
  "tools": [...]
}
```

---

## Configuration

### Backend Configuration

Edit `backend/.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/mcp_generator

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# AI Providers
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_AI_PROVIDER=anthropic

# App Settings
DEBUG=True
MAX_UPLOAD_SIZE=10485760  # 10MB
LOG_LEVEL=INFO
```

### Frontend Configuration

No configuration needed for development. For production:

```env
VITE_API_URL=https://your-backend-domain.com
```

### Docker Configuration

Edit `docker-compose.yml` to customize:

```yaml
services:
  postgres:
    environment:
      POSTGRES_DB: mcp_generator
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: change_me_in_production
    ports:
      - "5432:5432"

  backend:
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/mcp_generator
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8000:8000"

  frontend:
    ports:
      - "5173:5173"
```

---

## Deployment

### Production Deployment

#### Using Docker Compose

1. **Configure environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with production values
   ```

2. **Build and start services**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Run migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

#### Using Kubernetes

See `k8s/` directory for Kubernetes manifests (coming soon).

#### Using Cloud Providers

**AWS ECS:**
- Use provided ECS task definitions
- Configure RDS for PostgreSQL
- Use ALB for load balancing

**Google Cloud Run:**
- Deploy backend and frontend as separate services
- Use Cloud SQL for PostgreSQL
- Configure Cloud Load Balancer

**Azure Container Instances:**
- Deploy using provided ARM templates
- Use Azure Database for PostgreSQL
- Configure Application Gateway

### Reverse Proxy Configuration

#### Nginx

```nginx
server {
    listen 80;
    server_name mcp-portal.example.com;

    # Frontend
    location / {
        proxy_pass http://frontend:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # MCP SSE endpoint (requires special config)
    location /api/v1/mcp/serve/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;
    }
}
```

#### Caddy

```
mcp-portal.example.com {
    reverse_proxy /api/* backend:8000
    reverse_proxy /* frontend:5173
}
```

---

## Troubleshooting

### Common Issues

#### Can't Connect to localhost API from Docker

**Problem:** Trying to import from `http://localhost:8000/openapi.json` fails

**Solution:** Use `http://host.docker.internal:8000/openapi.json` instead

**Why:** Docker containers have their own network namespace. `localhost` refers to the container itself, not the host machine.

#### Anthropic API Errors in AI Sandbox

**Problem:** "Anthropic API key not configured" error

**Solution:**
1. Check `backend/.env` has `ANTHROPIC_API_KEY=sk-ant-xxxxx`
2. Restart backend: `docker-compose restart backend`
3. Or override in AI Sandbox UI

#### MCP Server Shows as Inactive After Deployment

**Problem:** Server deployed but shows inactive status

**Solution:**
1. Check Docker logs: `docker-compose logs backend`
2. Verify base URL is accessible
3. Check for port conflicts
4. Try restarting: Click "Restart" in Deployment page

#### Frontend Shows Blank Screen

**Problem:** White screen or no content

**Solution:**
1. Check browser console for errors
2. Verify backend is running: `curl http://localhost:8000/health`
3. Check CORS settings in backend `.env`
4. Restart frontend: `docker-compose restart frontend`

#### Database Connection Errors

**Problem:** Backend can't connect to PostgreSQL

**Solution:**
1. Verify PostgreSQL is running: `docker-compose ps postgres`
2. Check logs: `docker-compose logs postgres`
3. Verify connection string in `backend/.env`
4. Reset database: `docker-compose down -v && docker-compose up -d`

#### OpenAI API Errors

**Problem:** "Invalid API key" or connection errors

**Solution:**
1. Verify API key is correct
2. Check base URL (must include `/v1` for OpenAI)
3. For local models, ensure server is running
4. Test with curl:
   ```bash
   curl -X POST http://localhost:11434/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model":"llama2","messages":[{"role":"user","content":"hi"}]}'
   ```

#### Tool Execution Timeouts

**Problem:** Tools take too long or timeout

**Solution:**
1. Check if target API is responsive
2. Increase timeout in generated MCP code
3. Check network connectivity
4. Verify API authentication

### Debug Mode

Enable detailed logging:

```env
# backend/.env
DEBUG=True
LOG_LEVEL=DEBUG
```

View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database connectivity
docker-compose exec postgres psql -U postgres -d mcp_generator -c "SELECT 1;"

# Frontend (should return HTML)
curl http://localhost:5173
```

---

## Advanced Topics

### Custom MCP Server Templates

Modify code generation templates in `backend/app/services/mcp_generator.py`:

```python
def _generate_main_code(self, ...):
    # Customize generated code structure
    # Add custom imports
    # Modify function templates
    pass
```

### Adding Custom Authentication

Edit generated MCP servers to include auth:

```python
async def make_api_request(method, path, params, json_body):
    headers = {
        "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method=method,
            url=f"{BASE_URL}{path}",
            params=params,
            json=json_body,
            headers=headers
        )
        return response.json()
```

### Database Migrations

Create new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

### Monitoring and Logging

Integrate with logging services:

```python
# backend/app/config.py
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
```

### Performance Optimization

**Database:**
- Add indexes for frequently queried fields
- Use connection pooling
- Enable query caching

**Backend:**
- Enable response compression
- Use async operations
- Cache OpenAPI spec parsing

**Frontend:**
- Enable code splitting
- Lazy load routes
- Optimize bundle size

### Security Best Practices

1. **Environment Variables**
   - Never commit API keys
   - Use secrets management (Vault, AWS Secrets Manager)

2. **Input Validation**
   - Validate all user inputs
   - Sanitize file uploads
   - Check URL schemes

3. **API Security**
   - Add rate limiting
   - Implement authentication
   - Use HTTPS in production

4. **Generated Code**
   - Validate syntax before deployment
   - Sandbox tool execution
   - Log all API calls

### Extending the Platform

**Adding New AI Providers:**

1. Create provider service in `backend/app/services/`
2. Add configuration to `config.py`
3. Update API endpoints in `ai_testing.py`
4. Add UI controls in `AITestingPage.tsx`

**Custom Tool Types:**

1. Define new tool schemas
2. Update MCP generator templates
3. Add UI configuration options
4. Test with AI Sandbox

---

## Support and Community

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/yourusername/mcp-portal/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mcp-portal/discussions)
- **Email**: support@yourproject.com

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### License

MIT License - see [LICENSE](LICENSE) file.

---

**Built with ❤️ for the AI community**
