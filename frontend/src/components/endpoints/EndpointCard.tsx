import { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle2 } from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import ParameterConfig from './ParameterConfig';
import type { EndpointConfigWithDetails, ParameterConfigItem } from '@/types/endpoint';

interface EndpointCardProps {
  endpoint: EndpointConfigWithDetails;
  onChange: (endpoint: EndpointConfigWithDetails) => void;
}

function EndpointCard({ endpoint, onChange }: EndpointCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getMethodColor = (method: string) => {
    const colors: Record<string, string> = {
      GET: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      POST: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      PUT: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
      DELETE: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
      PATCH: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
    };
    return colors[method] || 'bg-gray-100 text-gray-800';
  };

  const handleSelectionChange = (checked: boolean) => {
    onChange({ ...endpoint, is_selected: checked });
    if (checked) {
      setIsExpanded(true);
    }
  };

  const handleParameterChange = (updatedParam: ParameterConfigItem) => {
    const updatedParams = endpoint.parameter_configurations?.map((param) =>
      param.name === updatedParam.name ? updatedParam : param
    );
    onChange({ ...endpoint, parameter_configurations: updatedParams || null });
  };

  const isConfigured = endpoint.is_selected && endpoint.mcp_description;
  const hasParameters = endpoint.parameter_configurations && endpoint.parameter_configurations.length > 0;

  return (
    <Card className={endpoint.is_selected ? 'border-2 border-primary/50 shadow-md bg-primary/5' : 'border-2 hover:border-border transition-all'}>
      <CardHeader className="pb-4">
        <div className="flex items-start gap-4">
          <div className="mt-1">
            <Checkbox
              checked={endpoint.is_selected}
              onCheckedChange={handleSelectionChange}
              className="w-5 h-5"
            />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <Badge className={`${getMethodColor(endpoint.http_method)} font-semibold px-2.5 py-0.5 text-xs`}>
                {endpoint.http_method}
              </Badge>
              <code className="text-sm font-mono font-medium break-all">{endpoint.path}</code>
              {endpoint.deprecated && (
                <Badge variant="destructive" className="text-xs font-semibold">
                  Deprecated
                </Badge>
              )}
              {isConfigured && (
                <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-100 dark:bg-green-900/30">
                  <CheckCircle2 className="w-3.5 h-3.5 text-green-600 dark:text-green-400" />
                  <span className="text-xs font-medium text-green-700 dark:text-green-400">Configured</span>
                </div>
              )}
            </div>
            <CardTitle className="text-base font-semibold">{endpoint.summary || 'No summary'}</CardTitle>
            {endpoint.description && (
              <CardDescription className="mt-1.5 text-sm">{endpoint.description}</CardDescription>
            )}
            {endpoint.tags.length > 0 && (
              <div className="flex gap-1.5 mt-2 flex-wrap">
                {endpoint.tags.map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs font-medium">
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
          </div>
          {endpoint.is_selected && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </Button>
          )}
        </div>
      </CardHeader>

      {endpoint.is_selected && isExpanded && (
        <CardContent className="space-y-5 pt-5 border-t bg-secondary/30">
          {/* MCP Tool Name */}
          <div className="space-y-2">
            <Label htmlFor={`tool-name-${endpoint.id}`} className="text-sm font-semibold">
              Tool Name <span className="text-xs text-muted-foreground font-normal">(optional)</span>
            </Label>
            <Input
              id={`tool-name-${endpoint.id}`}
              placeholder={`${endpoint.http_method.toLowerCase()}_${endpoint.path.replace(/[^a-z0-9]/gi, '_')}`}
              value={endpoint.mcp_tool_name || ''}
              onChange={(e) =>
                onChange({ ...endpoint, mcp_tool_name: e.target.value || null })
              }
              className="h-10 border-2 rounded-xl"
            />
            <p className="text-xs text-muted-foreground">
              Custom name for the MCP tool. If not provided, a name will be generated.
            </p>
          </div>

          {/* MCP Description */}
          <div className="space-y-2">
            <Label htmlFor={`mcp-desc-${endpoint.id}`} className="text-sm font-semibold">
              Tool Description <span className="text-destructive font-semibold">*</span>
            </Label>
            <Textarea
              id={`mcp-desc-${endpoint.id}`}
              placeholder="Describe what this tool does in the context of MCP..."
              value={endpoint.mcp_description || ''}
              onChange={(e) =>
                onChange({ ...endpoint, mcp_description: e.target.value || null })
              }
              rows={3}
              className="border-2 rounded-xl resize-none"
            />
            {endpoint.is_selected && !endpoint.mcp_description && (
              <p className="text-sm text-destructive font-medium flex items-center gap-1.5">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-destructive"></span>
                Description is required for selected endpoints
              </p>
            )}
          </div>

          {/* Parameters Configuration */}
          {hasParameters && (
            <div className="space-y-3 p-4 rounded-2xl bg-card border">
              <div className="flex items-center justify-between">
                <Label className="text-sm font-semibold">Parameters Configuration</Label>
                <Badge variant="secondary" className="px-2.5 py-0.5 font-medium text-xs">
                  {endpoint.parameter_configurations?.length} parameter(s)
                </Badge>
              </div>
              <div className="space-y-3">
                {endpoint.parameter_configurations?.map((param) => (
                  <ParameterConfig
                    key={param.name}
                    parameter={param}
                    onChange={handleParameterChange}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Summary */}
          <div className="pt-3 border-t">
            <p className="text-xs text-muted-foreground">
              {hasParameters
                ? `This endpoint has ${endpoint.parameter_configurations?.length} parameter(s). Configure each parameter's description and whether it should be mandatory.`
                : 'This endpoint has no parameters.'}
            </p>
          </div>
        </CardContent>
      )}
    </Card>
  );
}

export default EndpointCard;
