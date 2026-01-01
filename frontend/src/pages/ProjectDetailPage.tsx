import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, FileCode, Loader2 } from 'lucide-react';
import Header from '@/components/layout/Header';
import SpecUploader from '@/components/swagger/SpecUploader';
import SpecViewer from '@/components/swagger/SpecViewer';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useProject } from '@/hooks/useProjects';
import { useSwaggerSpecs } from '@/hooks/useSwaggerSpec';

function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [isUploaderOpen, setIsUploaderOpen] = useState(false);

  const { data: project, isLoading: isProjectLoading } = useProject(projectId || '');
  const { data: specs, isLoading: isSpecsLoading, refetch } = useSwaggerSpecs(projectId || '');

  if (isProjectLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary" />
            <p className="text-muted-foreground mt-4">Loading project...</p>
          </div>
        </main>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="text-center py-12">
            <p className="text-destructive">Project not found</p>
            <Button onClick={() => navigate('/')} className="mt-4">
              Go Home
            </Button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-4 py-8">
        {/* Back Button & Project Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Projects
          </Button>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">{project.name}</h1>
              {project.description && (
                <p className="text-lg text-muted-foreground">{project.description}</p>
              )}
              <div className="flex items-center gap-4 mt-4 text-sm text-muted-foreground">
                <span>{project.swagger_specs_count} API Specs</span>
                <span>•</span>
                <span>{project.generated_servers_count} MCP Servers</span>
              </div>
            </div>
            <Button onClick={() => setIsUploaderOpen(true)} size="lg">
              <Plus className="w-4 h-4 mr-2" />
              Import Spec
            </Button>
          </div>
        </div>

        {/* Swagger Specs Section */}
        {isSpecsLoading ? (
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary" />
            <p className="text-muted-foreground mt-4">Loading specifications...</p>
          </div>
        ) : specs && specs.length > 0 ? (
          <div className="space-y-6">
            {specs.map((spec) => (
              <SpecViewer key={spec.id} spec={spec} />
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16">
              <div className="flex items-center justify-center w-16 h-16 rounded-full bg-muted mb-4">
                <FileCode className="w-8 h-8 text-muted-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-2">No API Specifications Yet</h3>
              <p className="text-muted-foreground mb-6 text-center max-w-md">
                Import your first Swagger/OpenAPI specification to get started with MCP server generation
              </p>
              <Button onClick={() => setIsUploaderOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Import Your First Spec
              </Button>
            </CardContent>
          </Card>
        )}
      </main>

      <SpecUploader
        projectId={projectId || ''}
        open={isUploaderOpen}
        onOpenChange={setIsUploaderOpen}
        onSuccess={() => refetch()}
      />
    </div>
  );
}

export default ProjectDetailPage;
