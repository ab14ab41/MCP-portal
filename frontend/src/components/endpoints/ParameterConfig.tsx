import { AlertCircle } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import type { ParameterConfigItem } from '@/types/endpoint';

interface ParameterConfigProps {
  parameter: ParameterConfigItem;
  onChange: (parameter: ParameterConfigItem) => void;
  error?: string;
}

function ParameterConfig({ parameter, onChange, error }: ParameterConfigProps) {
  const getLocationColor = (location: string) => {
    const colors: Record<string, string> = {
      path: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      query: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      header: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
      cookie: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
    };
    return colors[location] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="border rounded-lg p-4 space-y-4 bg-muted/30">
      {/* Parameter Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <code className="text-sm font-mono font-semibold">{parameter.name}</code>
            <Badge variant="outline" className={getLocationColor(parameter.location)}>
              {parameter.location}
            </Badge>
            <Badge variant="outline">{parameter.type}</Badge>
            {parameter.deprecated && (
              <Badge variant="destructive" className="text-xs">
                Deprecated
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>
              Spec: {parameter.required ? 'Required ✓' : 'Optional'}
            </span>
          </div>
        </div>
      </div>

      {/* Mandatory Toggle */}
      <div className="flex items-start space-x-3 p-3 rounded-md bg-background border">
        <Checkbox
          id={`mandatory-${parameter.name}`}
          checked={parameter.user_required}
          onCheckedChange={(checked) =>
            onChange({ ...parameter, user_required: checked as boolean })
          }
        />
        <div className="flex-1">
          <Label
            htmlFor={`mandatory-${parameter.name}`}
            className="font-medium cursor-pointer flex items-center gap-2"
          >
            Make this parameter mandatory
            {parameter.user_required !== parameter.required && (
              <AlertCircle className="w-4 h-4 text-orange-500" />
            )}
          </Label>
          <p className="text-xs text-muted-foreground mt-1">
            {parameter.user_required
              ? 'This parameter will be required in the generated MCP tool'
              : 'This parameter will be optional in the generated MCP tool'}
          </p>
          {parameter.user_required !== parameter.required && (
            <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
              ⚠ You are overriding the original specification
            </p>
          )}
        </div>
      </div>

      {/* Parameter Description */}
      <div className="space-y-2">
        <Label htmlFor={`desc-${parameter.name}`}>
          Description <span className="text-destructive">*</span>
        </Label>
        <Textarea
          id={`desc-${parameter.name}`}
          placeholder="Describe what this parameter does..."
          value={parameter.description}
          onChange={(e) => onChange({ ...parameter, description: e.target.value })}
          rows={3}
        />
        {error && <p className="text-sm text-destructive">{error}</p>}
      </div>

      {/* Schema Info */}
      {parameter.schema.default !== undefined && (
        <div className="text-xs text-muted-foreground">
          Default: <code className="font-mono bg-muted px-1 py-0.5 rounded">
            {JSON.stringify(parameter.schema.default)}
          </code>
        </div>
      )}
    </div>
  );
}

export default ParameterConfig;
