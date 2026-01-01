# MCP Portal

<div align="center">

![MCP Portal](https://img.shields.io/badge/MCP-Portal-blue?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-18-blue?style=for-the-badge&logo=react)
![Python](https://img.shields.io/badge/Python-3.11+-yellow?style=for-the-badge&logo=python)

**Transform Swagger/OpenAPI specifications into deployable MCP servers with AI-powered testing**

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](#contributing)

</div>

---

## 🌟 Features

### 📥 Flexible API Import
- **Multiple Import Methods**: Upload files, fetch from URLs, paste content, or connect to live API endpoints
- **OpenAPI Support**: Full support for OpenAPI 2.0 (Swagger) and 3.0+ specifications
- **Automatic Parsing**: Smart detection and parsing with reference resolution
- **Docker-Aware**: Special handling for `localhost` → `host.docker.internal` in Docker environments

### ⚙️ Advanced Configuration
- **Endpoint Selection**: Choose exactly which API endpoints to expose in your MCP server
- **Parameter Customization**: Override original spec requirements - make optional parameters mandatory or vice versa
- **Custom Descriptions**: Add AI-friendly descriptions for methods and parameters
- **Base URL Management**: Easily update API base URLs with automatic MCP re-registration

### 🤖 AI-Powered Testing (AI Sandbox)
- **Multi-Provider Support**:
  - **Anthropic Claude** (Haiku, Sonnet, Opus)
  - **OpenAI-Compatible APIs** (OpenAI, Azure OpenAI, local models)
- **Multi-MCP Testing**: Test with multiple MCP servers simultaneously
- **Tool Execution**: Automatic tool discovery and execution
- **Real-time Chat**: Interactive conversation interface with tool call visualization
- **Custom Configuration**: Override API keys, models, and base URLs per session

### 🚀 Deployment & Management
- **One-Click Deployment**: Deploy MCP servers as HTTP-streamable endpoints
- **Server Management**: Start, stop, restart, and delete deployed servers
- **Real-time Status**: Monitor active/inactive servers
- **MCP Info Viewer**: Inspect available tools and schemas
- **Search & Filter**: Quickly find servers by name or project
- **Copy Endpoints**: One-click copy of MCP endpoint URLs

### 🎨 Modern UI/UX
- **Beautiful Interface**: Modern, responsive design with Tailwind CSS
- **Dark/Light Mode**: System-aware theme switching
- **Real-time Updates**: Instant UI updates with React Query
- **Search Everywhere**: Search functionality across all pages
- **Smart Empty States**: Helpful guidance when getting started

---

## 🏗️ Architecture

### Tech Stack

#### Backend
- **FastAPI** - Modern, high-performance Python web framework
- **SQLAlchemy (Async)** - Powerful ORM with async support
- **PostgreSQL 15+** - Robust database with JSONB for flexible schemas
- **Prance** - OpenAPI parser with automatic reference resolution
- **Anthropic SDK** - Claude AI integration
- **OpenAI SDK** - OpenAI-compatible model support
- **FastMCP** - MCP server generation framework

#### Frontend
- **React 18** - Modern UI library with hooks
- **TypeScript** - Type-safe development
- **Vite** - Lightning-fast build tool and HMR
- **TanStack Query** - Powerful server state management
- **Tailwind CSS** - Utility-first styling
- **React Hook Form + Zod** - Form validation
- **Lucide React** - Beautiful icon library

#### Infrastructure
- **Docker & Docker Compose** - Containerization and orchestration
- **Alembic** - Database migrations
- **Nginx** (optional) - Production reverse proxy

---

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- (Optional) **Node.js 20+** for local frontend development
- (Optional) **Python 3.11+** for local backend development

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mcp-portal.git
   cd mcp-portal
   ```

2. **Configure environment variables**
   ```bash
   cp backend/.env.example backend/.env
   ```

   Edit `backend/.env` and add your API keys:
   ```env
   # Required for AI Sandbox (Anthropic)
   ANTHROPIC_API_KEY=sk-ant-xxxxx

   # Optional for AI Sandbox (OpenAI)
   OPENAI_API_KEY=sk-xxxxx
   OPENAI_BASE_URL=https://api.openai.com/v1
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - **Frontend**: http://localhost:5173
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

That's it! 🎉 The application is now running.

---

## 📖 Documentation

For complete documentation, see:
- **[📘 Complete Documentation](DOCUMENTATION.md)** - In-depth guide covering all features, API reference, and advanced topics
- **[🤖 AI Sandbox Guide](AI_TESTING_SETUP.md)** - Detailed guide for testing MCPs with multiple AI providers

### Basic Workflow

#### 1️⃣ Create a Project
Navigate to the **Projects** page and create a new project to organize your MCP servers.

#### 2️⃣ Import Swagger/OpenAPI Spec
Choose your preferred import method:
- **Upload** a `.json` or `.yaml` file
- **Fetch from URL** (e.g., `http://host.docker.internal:8000/openapi.json`)
- **Paste** OpenAPI spec content directly
- **Connect** to a live API endpoint

💡 **Tip**: When running APIs locally in Docker, use `host.docker.internal` instead of `localhost`.

#### 3️⃣ Configure Endpoints
- Select which endpoints to expose in your MCP server
- Add AI-friendly descriptions for each endpoint
- Customize parameter requirements:
  - Make optional parameters mandatory
  - Make required parameters optional
- Review request/response schemas

#### 4️⃣ Generate & Deploy
- Click **Generate MCP** to create your Python server
- **Preview** the generated code
- **Deploy** to make it accessible via HTTP
- Your MCP is now ready to use!

#### 5️⃣ Test with AI (AI Sandbox)
- Navigate to **AI Sandbox**
- Select one or more deployed MCP servers
- Choose your AI provider (Anthropic or OpenAI)
- Start chatting! The AI can automatically use available tools

---

## 🎯 Use Cases

### 1. **Convert REST APIs to AI Tools**
Transform any REST API into AI-usable tools:
```
REST API → Swagger/OpenAPI → MCP Server → AI Agent
```

### 2. **Multi-API Testing**
Test complex workflows that span multiple APIs:
- Select multiple MCP servers in AI Sandbox
- AI can use tools from all selected servers
- Test cross-API integrations naturally

### 3. **Custom AI Agents**
Build specialized AI agents with curated tool sets:
- Fine-tune which endpoints are available
- Add context-rich descriptions
- Control parameter requirements

### 4. **API Exploration**
Use AI to explore and understand new APIs:
- Import API spec
- Let AI discover and explain available endpoints
- Test API calls interactively

---

## 🔧 Configuration

### Environment Variables

#### Backend (`backend/.env`)
```env
# App Settings
DEBUG=True
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/mcp_generator

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB

# AI Providers
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_AI_PROVIDER=anthropic
```

**Log Levels:**
- `DEBUG` - Detailed information for diagnosing issues (shows all logs including tool schemas)
- `INFO` - General informational messages (default, recommended for production)
- `WARNING` - Warning messages about potential issues
- `ERROR` - Error messages when something goes wrong
- `CRITICAL` - Critical errors that may prevent the application from running

#### Frontend
The frontend automatically connects to `http://localhost:8000` in development. For production, set `VITE_API_URL` in your build environment.

---

## 📂 Project Structure

```
mcp-portal/
├── backend/
│   ├── app/
│   │   ├── api/v1/              # API endpoints
│   │   │   ├── projects.py      # Project management
│   │   │   ├── swagger_specs.py # Swagger spec handling
│   │   │   ├── endpoint_configs.py # Endpoint configuration
│   │   │   ├── generation.py    # MCP generation & deployment
│   │   │   ├── mcp_serve.py     # MCP serving endpoints
│   │   │   └── ai_testing.py    # AI Sandbox API
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   │   ├── swagger_parser.py # OpenAPI parsing
│   │   │   ├── mcp_generator.py  # MCP code generation
│   │   │   ├── mcp_serving.py    # MCP server management
│   │   │   └── ai_agent_tester.py # AI testing service
│   │   ├── repositories/        # Data access layer
│   │   ├── config.py            # Application settings
│   │   ├── database.py          # Database setup
│   │   └── main.py              # FastAPI app
│   ├── alembic/                 # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable components
│   │   │   ├── ui/              # UI primitives
│   │   │   ├── layout/          # Layout components
│   │   │   └── swagger/         # Swagger-specific
│   │   ├── pages/               # Page components
│   │   │   ├── HomePage.tsx     # Projects page
│   │   │   ├── ProjectPage.tsx  # Project detail
│   │   │   ├── DeployedMCPsPage.tsx # Deployment management
│   │   │   └── AITestingPage.tsx    # AI Sandbox
│   │   ├── hooks/               # Custom React hooks
│   │   ├── lib/                 # Utilities
│   │   └── types/               # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── README.md
└── DOCUMENTATION.md
```

---

## 🔌 API Reference

### Core Endpoints

#### Projects
```http
POST   /api/v1/projects                    # Create project
GET    /api/v1/projects                    # List projects
GET    /api/v1/projects/{id}               # Get project
PUT    /api/v1/projects/{id}               # Update project
DELETE /api/v1/projects/{id}               # Delete project
```

#### Swagger Specs
```http
POST   /api/v1/projects/{id}/swagger-specs/upload      # Upload file
POST   /api/v1/projects/{id}/swagger-specs/from-url    # From URL
POST   /api/v1/projects/{id}/swagger-specs/from-content # Paste
GET    /api/v1/swagger-specs/{id}                      # Get spec
PATCH  /api/v1/swagger-specs/{id}/base-url             # Update base URL
DELETE /api/v1/swagger-specs/{id}                      # Delete spec
```

#### MCP Generation & Deployment
```http
POST   /api/v1/swagger-specs/{id}/generate-mcp              # Generate
POST   /api/v1/swagger-specs/generated-servers/{id}/deploy  # Deploy
POST   /api/v1/swagger-specs/generated-servers/{id}/undeploy # Stop
DELETE /api/v1/swagger-specs/generated-servers/{id}         # Delete
GET    /api/v1/swagger-specs/deployed-servers               # List deployed
```

#### AI Sandbox
```http
GET    /api/v1/ai-testing/deployed-servers/{id}/tools  # Get tools
POST   /api/v1/ai-testing/deployed-servers/{id}/test   # Test with AI
POST   /api/v1/ai-testing/deployed-servers/{id}/execute-tool # Execute tool
```

#### MCP Serving
```http
GET    /api/v1/mcp/serve/{id}      # MCP SSE endpoint
GET    /api/v1/mcp/serve/{id}/info # MCP info (tools list)
```

For detailed API documentation, visit http://localhost:8000/docs when running.

---

## 🧪 Development

### Local Backend Setup

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start PostgreSQL**
   ```bash
   docker-compose up postgres -d
   ```

4. **Run migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start backend**
   ```bash
   uvicorn app.main:app --reload
   ```

### Local Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start dev server**
   ```bash
   npm run dev
   ```

### Database Migrations

```bash
# Create migration
cd backend
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: Can't connect to `localhost` API from Docker
- **Solution**: Use `host.docker.internal` instead of `localhost` when importing specs

**Issue**: Anthropic API errors in AI Sandbox
- **Solution**: Ensure `ANTHROPIC_API_KEY` is set in `backend/.env` and restart backend

**Issue**: MCP server shows as inactive after deployment
- **Solution**: Check Docker logs: `docker-compose logs backend`

**Issue**: Frontend shows blank screen
- **Solution**: Check browser console for errors, ensure backend is running

**Issue**: Database connection errors
- **Solution**: Ensure PostgreSQL is running: `docker-compose up postgres -d`

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Follow existing code style
- Keep PRs focused and small

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic** - Claude AI and MCP Protocol
- **FastAPI** - Amazing Python web framework
- **React** - Powerful UI library
- **FastMCP** - Simplified MCP server creation
- **Prance** - Excellent OpenAPI parser

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mcp-portal/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mcp-portal/discussions)
- **Email**: support@yourproject.com

---

<div align="center">

**Built with ❤️ for the AI community**

[⬆ Back to Top](#mcp-portal)

</div>
"# MCP-portal" 
