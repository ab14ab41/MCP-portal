import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, Sparkles } from 'lucide-react';
import Header from '@/components/layout/Header';
import ProjectCard from '@/components/projects/ProjectCard';
import CreateProjectModal from '@/components/projects/CreateProjectModal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useProjects, useDeleteProject } from '@/hooks/useProjects';

function HomePage() {
  const navigate = useNavigate();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const { data: projects, isLoading, error } = useProjects({ search: searchQuery || undefined });
  const deleteProject = useDeleteProject();

  const handleDelete = async (id: string) => {
    try {
      await deleteProject.mutateAsync(id);
    } catch (error) {
      console.error('Failed to delete project:', error);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <div className="relative pt-24 pb-16 px-6">
        <div className="container mx-auto max-w-5xl text-center">
          <h1 className="text-6xl md:text-7xl font-bold mb-6 tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
            Transform APIs into
            <br />
            <span className="text-primary">MCP Servers</span>
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-10 max-w-3xl mx-auto font-light">
            Build powerful Model Context Protocol servers from your OpenAPI specifications with ease
          </p>
          <div className="flex items-center justify-center gap-4">
            <Button
              onClick={() => setIsCreateModalOpen(true)}
              size="lg"
              className="h-12 px-8 bg-primary hover:bg-primary/90 text-white font-semibold rounded-full shadow-lg shadow-primary/30"
            >
              <Plus className="w-5 h-5 mr-2" />
              Create Project
            </Button>
            <Button
              onClick={() => navigate('/documentation')}
              variant="outline"
              size="lg"
              className="h-12 px-8 font-semibold rounded-full"
            >
              Learn More
            </Button>
          </div>
        </div>
      </div>

      <main className="container mx-auto px-6 pb-20 max-w-7xl">
        {/* Search Bar */}
        <div className="mb-12">
          <div className="relative max-w-2xl mx-auto">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search your projects..."
              className="pl-12 h-12 bg-background border-2 rounded-xl shadow-sm"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        {/* Projects Section */}
        {isLoading ? (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent"></div>
            <p className="text-muted-foreground mt-6 text-lg">Loading your projects...</p>
          </div>
        ) : error ? (
          <div className="text-center py-20">
            <p className="text-destructive text-xl">Failed to load projects</p>
          </div>
        ) : projects && projects.length > 0 ? (
          <div>
            <h2 className="text-3xl font-semibold mb-8">Your Projects</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((project) => (
                <ProjectCard
                  key={project.id}
                  project={project}
                  onDelete={handleDelete}
                />
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-32">
            <div className="flex justify-center mb-8">
              <div className="w-28 h-28 rounded-3xl bg-secondary/50 flex items-center justify-center">
                <Sparkles className="w-14 h-14 text-muted-foreground" />
              </div>
            </div>
            <h3 className="text-4xl font-semibold mb-4">
              No Projects Yet
            </h3>
            <p className="text-xl text-muted-foreground mb-10 max-w-lg mx-auto font-light">
              Start building by creating your first project and transforming your APIs into MCP servers
            </p>
            <Button
              onClick={() => setIsCreateModalOpen(true)}
              size="lg"
              className="h-12 px-10 bg-primary hover:bg-primary/90 text-white font-semibold rounded-full shadow-lg shadow-primary/30"
            >
              <Plus className="w-5 h-5 mr-2" />
              Create Your First Project
            </Button>
          </div>
        )}
      </main>

      <CreateProjectModal
        open={isCreateModalOpen}
        onOpenChange={setIsCreateModalOpen}
      />
    </div>
  );
}

export default HomePage;
