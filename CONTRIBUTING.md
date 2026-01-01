# Contributing to MCP Portal

Thank you for your interest in contributing to MCP Portal! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for everyone. Please be respectful and constructive in all interactions.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## Getting Started

### Prerequisites

- **Git** - Version control
- **Docker** & **Docker Compose** - For running the full stack
- **Node.js 20+** - For frontend development
- **Python 3.11+** - For backend development
- **PostgreSQL 15+** - Database (can use Docker)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/mcp-portal.git
   cd mcp-portal
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/mcp-portal.git
   ```

### Development Setup

#### Quick Start (Docker)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

#### Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL
docker-compose up postgres -d

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Development Workflow

### Branch Naming

Use descriptive branch names with prefixes:

- `feature/` - New features
  - Example: `feature/add-graphql-support`
- `fix/` - Bug fixes
  - Example: `fix/deployment-timeout`
- `docs/` - Documentation changes
  - Example: `docs/update-api-reference`
- `refactor/` - Code refactoring
  - Example: `refactor/mcp-generator-service`
- `test/` - Adding or updating tests
  - Example: `test/add-endpoint-config-tests`

### Making Changes

1. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write clear, concise code
   - Follow existing code style
   - Add tests for new features
   - Update documentation

3. **Test your changes:**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm test

   # Type checking
   npm run type-check
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Coding Standards

### Backend (Python)

**Style Guide:**
- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use type hints for function parameters and return values
- Maximum line length: 100 characters

**Code Formatting:**
```bash
# Format code
black backend/

# Check formatting
black --check backend/

# Sort imports
isort backend/
```

**Linting:**
```bash
# Run flake8
flake8 backend/ --max-line-length=100

# Run mypy
mypy backend/
```

**Best Practices:**
```python
# Good: Type hints and docstrings
async def create_project(
    name: str,
    description: str,
    db: AsyncSession
) -> Project:
    """
    Create a new project.

    Args:
        name: Project name
        description: Project description
        db: Database session

    Returns:
        Created project instance
    """
    project = Project(name=name, description=description)
    db.add(project)
    await db.commit()
    return project
```

### Frontend (TypeScript/React)

**Style Guide:**
- Use TypeScript for all new code
- Follow [Airbnb React/JSX Style Guide](https://airbnb.io/javascript/react/)
- Use functional components with hooks
- Use meaningful variable and function names

**Code Formatting:**
```bash
# Format code
npm run format

# Check formatting
npm run format:check

# Lint
npm run lint
```

**Best Practices:**
```typescript
// Good: Typed components with clear interfaces
interface ProjectCardProps {
  project: Project;
  onDelete: (id: string) => void;
}

export function ProjectCard({ project, onDelete }: ProjectCardProps) {
  const handleDelete = () => {
    onDelete(project.id);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{project.name}</CardTitle>
      </CardHeader>
      <CardContent>
        {project.description}
      </CardContent>
    </Card>
  );
}
```

**Component Structure:**
- One component per file
- Co-locate tests with components
- Use index files for exports
- Keep components small and focused

### Database Migrations

**Creating Migrations:**
```bash
cd backend
alembic revision --autogenerate -m "Add user_preferences table"
```

**Migration Best Practices:**
- Always review auto-generated migrations
- Test migrations both up and down
- Never modify existing migrations
- Include data migrations when needed
- Add comments for complex changes

**Example Migration:**
```python
"""Add user_preferences table

Revision ID: abc123
Revises: def456
Create Date: 2025-01-15 10:00:00.000000
"""

def upgrade():
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('preferences', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    # Add index for performance
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'])

def downgrade():
    op.drop_index('ix_user_preferences_user_id', 'user_preferences')
    op.drop_table('user_preferences')
```

## Commit Guidelines

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks

**Examples:**
```bash
# Feature
git commit -m "feat(ai-sandbox): add multi-provider support"

# Bug fix
git commit -m "fix(deployment): resolve timeout issue on large specs"

# Documentation
git commit -m "docs(readme): update installation instructions"

# Breaking change
git commit -m "feat(api): change endpoint parameter format

BREAKING CHANGE: endpoint configuration now uses snake_case"
```

### Commit Best Practices

- Write clear, descriptive commit messages
- Keep commits focused on a single change
- Reference issue numbers when applicable
- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")

## Pull Request Process

### Before Submitting

1. **Sync with upstream:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all tests:**
   ```bash
   # Backend
   cd backend && pytest

   # Frontend
   cd frontend && npm test
   ```

3. **Check code quality:**
   ```bash
   # Backend
   black --check backend/
   flake8 backend/

   # Frontend
   npm run lint
   npm run type-check
   ```

4. **Update documentation** if needed

### Creating a Pull Request

1. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a PR on GitHub:**
   - Use a clear, descriptive title
   - Reference related issues
   - Provide detailed description
   - Add screenshots for UI changes
   - List any breaking changes

**PR Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Changes Made
- Added X feature
- Fixed Y bug
- Updated Z documentation

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### PR Review Process

1. **Automated Checks:**
   - CI/CD pipeline runs tests
   - Code quality checks
   - Build verification

2. **Code Review:**
   - At least one approval required
   - Address reviewer feedback
   - Make requested changes

3. **Merge:**
   - Squash and merge (default)
   - Maintainer will merge when approved

## Testing

### Backend Testing

**Running Tests:**
```bash
cd backend

# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_projects.py

# Specific test
pytest tests/test_projects.py::test_create_project
```

**Writing Tests:**
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_project(client: AsyncClient):
    """Test project creation endpoint."""
    response = await client.post(
        "/api/v1/projects",
        json={
            "name": "Test Project",
            "description": "Test description"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
```

### Frontend Testing

**Running Tests:**
```bash
cd frontend

# All tests
npm test

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage
```

**Writing Tests:**
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { ProjectCard } from './ProjectCard';

describe('ProjectCard', () => {
  it('renders project information', () => {
    const project = {
      id: '1',
      name: 'Test Project',
      description: 'Test description'
    };

    render(<ProjectCard project={project} onDelete={() => {}} />);

    expect(screen.getByText('Test Project')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });

  it('calls onDelete when delete button clicked', () => {
    const onDelete = jest.fn();
    const project = { id: '1', name: 'Test', description: 'Test' };

    render(<ProjectCard project={project} onDelete={onDelete} />);

    fireEvent.click(screen.getByRole('button', { name: /delete/i }));

    expect(onDelete).toHaveBeenCalledWith('1');
  });
});
```

### Integration Testing

Test full workflows end-to-end:
```python
@pytest.mark.asyncio
async def test_full_mcp_workflow(client: AsyncClient, db: AsyncSession):
    """Test complete MCP generation workflow."""
    # 1. Create project
    project_response = await client.post("/api/v1/projects", json={...})
    project_id = project_response.json()["id"]

    # 2. Upload spec
    spec_response = await client.post(
        f"/api/v1/projects/{project_id}/swagger-specs/upload",
        files={"file": ("spec.json", spec_content, "application/json")}
    )
    spec_id = spec_response.json()["id"]

    # 3. Configure endpoints
    config_response = await client.post(
        f"/api/v1/swagger-specs/{spec_id}/endpoint-configurations/batch",
        json={"configurations": [...]}
    )

    # 4. Generate MCP
    gen_response = await client.post(
        f"/api/v1/swagger-specs/{spec_id}/generate-mcp",
        json={...}
    )

    # 5. Verify generation
    assert gen_response.status_code == 201
    assert "python_code" in gen_response.json()
```

## Documentation

### Updating Documentation

When making changes:

1. **Code Documentation:**
   - Add docstrings to functions/classes
   - Update type hints
   - Add inline comments for complex logic

2. **API Documentation:**
   - FastAPI auto-generates OpenAPI docs
   - Add description parameters to endpoints
   - Document request/response models

3. **User Documentation:**
   - Update README.md for major changes
   - Update DOCUMENTATION.md for detailed changes
   - Add examples and use cases

4. **Developer Documentation:**
   - Update architecture diagrams if needed
   - Document new patterns or conventions
   - Add troubleshooting tips

### Documentation Standards

**Code Comments:**
```python
# Good: Explain why, not what
# Use retry logic because API is rate-limited
retry_count = 3

# Bad: State the obvious
# Set retry count to 3
retry_count = 3
```

**Docstrings:**
```python
def parse_openapi_spec(spec_content: str, format: str) -> dict:
    """
    Parse OpenAPI specification from string content.

    Supports both OpenAPI 2.0 (Swagger) and 3.0+ specifications.
    Automatically resolves $ref references within the spec.

    Args:
        spec_content: Raw specification content as string
        format: Format of content ('json' or 'yaml')

    Returns:
        Parsed and resolved specification as dictionary

    Raises:
        ValueError: If spec_content is invalid or format is unsupported
        ParseError: If specification cannot be parsed

    Example:
        >>> spec = parse_openapi_spec(json_content, 'json')
        >>> print(spec['info']['title'])
        'My API'
    """
```

## Getting Help

### Resources

- **Documentation**: [DOCUMENTATION.md](DOCUMENTATION.md)
- **Issues**: [GitHub Issues](https://github.com/OWNER/mcp-portal/issues)
- **Discussions**: [GitHub Discussions](https://github.com/OWNER/mcp-portal/discussions)

### Asking Questions

When asking for help:

1. Search existing issues first
2. Provide clear, detailed information
3. Include relevant code snippets
4. Share error messages and logs
5. Describe what you've already tried

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- Release notes for significant contributions
- Project acknowledgments

Thank you for contributing to MCP Portal!
