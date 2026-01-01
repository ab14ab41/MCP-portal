# MCP Portal - Quick Start Guide

## What's Been Built So Far

### Phase 1: Foundation ✅
- Complete backend structure with FastAPI
- PostgreSQL database with 4 tables
- Alembic migrations setup
- React + TypeScript frontend with Vite
- Tailwind CSS + shadcn/ui components
- Docker Compose for full-stack orchestration

### Phase 2: Project Management ✅
- **Backend API** (fully functional):
  - `POST /api/v1/projects` - Create project
  - `GET /api/v1/projects` - List projects with search
  - `GET /api/v1/projects/{id}` - Get project with stats
  - `PUT /api/v1/projects/{id}` - Update project
  - `DELETE /api/v1/projects/{id}` - Delete project

- **Frontend UI** (modern & responsive):
  - Beautiful header with MCP Portal branding
  - Project cards with stats (API specs & MCP servers count)
  - Create project modal with form validation
  - Search functionality
  - Delete with confirmation
  - Empty state with call-to-action
  - Loading and error states
  - Responsive grid layout

## Quick Start

### Option 1: Docker (Recommended)

1. **Start the entire stack**:
   ```bash
   cd mcp-server-generator
   docker-compose up -d
   ```

2. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

3. **View logs**:
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

### Option 2: Local Development

#### Backend

1. **Install dependencies**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL**:
   ```bash
   docker-compose up postgres -d
   ```

3. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

4. **Start backend**:
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

## Testing the Application

### Test Backend API

1. **Check health**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Create a project**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/projects \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Project", "description": "My first project"}'
   ```

3. **List projects**:
   ```bash
   curl http://localhost:8000/api/v1/projects
   ```

4. **View API docs**:
   Open http://localhost:8000/docs in your browser

### Test Frontend UI

1. **Open the app**: http://localhost:5173

2. **Create a project**:
   - Click "New Project" button
   - Fill in project name and description
   - Click "Create Project"

3. **Test search**:
   - Type in the search box
   - Projects filter in real-time

4. **Delete a project**:
   - Hover over a project card
   - Click the trash icon (appears on hover)
   - Confirm deletion

## Current Features Working

- ✅ Create projects with name and description
- ✅ List all projects with beautiful cards
- ✅ Search projects by name
- ✅ View project statistics (specs count, servers count)
- ✅ Delete projects with confirmation
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Modern UI with smooth animations
- ✅ Form validation
- ✅ Loading and error states
- ✅ Empty state with helpful message

## Next Steps (Phases 3-6)

### Phase 3: Swagger/OpenAPI Parsing
- Upload Swagger specs (file, URL, paste, API)
- Parse with Prance (2.0 and 3.0+ support)
- Display all endpoints with parameters

### Phase 4: Endpoint Configuration
- Select endpoints to expose
- Add descriptions
- **Parameter mandatory override** (can mark as required/optional)

### Phase 5: MCP Generation
- Generate Python MCP server code
- Preview generated code
- Download as file or ZIP

### Phase 6: Polish & Testing
- Error handling improvements
- Unit and integration tests
- E2E tests
- Performance optimization

## Troubleshooting

### Port Already in Use

```bash
# Stop all containers
docker-compose down

# Remove volumes if needed
docker-compose down -v
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres
```

### Frontend Won't Load

```bash
# Check if backend is running
curl http://localhost:8000/health

# Restart frontend
docker-compose restart frontend
```

## Project Structure

```
mcp-server-generator/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # ✅ Projects API
│   │   ├── models/          # ✅ All 4 tables
│   │   ├── schemas/         # ✅ Pydantic schemas
│   │   ├── repositories/    # ✅ Data access
│   │   ├── services/        # 🔜 Parsing & generation
│   │   └── utils/           # ✅ Exceptions
│   └── alembic/             # ✅ Migrations
├── frontend/
│   └── src/
│       ├── components/      # ✅ Modern UI components
│       ├── hooks/           # ✅ React Query hooks
│       └── pages/           # ✅ HomePage
└── docker-compose.yml       # ✅ Full stack
```

Legend:
- ✅ Complete
- 🔜 Coming soon

## Need Help?

The application is working and ready for Phase 3! The current implementation includes:
- Full backend API for project management
- Beautiful, modern frontend interface
- Complete database schema
- Docker setup for easy deployment

Ready to continue with Swagger parsing? Let me know!
