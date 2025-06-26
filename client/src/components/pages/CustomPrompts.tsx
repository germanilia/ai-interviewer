import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { api, CustomPrompt } from '@/lib/api';
import { CustomPromptDialog } from '@/components/dialogs/CustomPromptDialog';

const PROMPT_TYPE_LABELS = {
  evaluation: 'Evaluation',
  judge: 'Judge',
  guardrails: 'Guardrails'
} as const;

const PROMPT_TYPE_DESCRIPTIONS = {
  evaluation: 'Initial response generation using a smaller, faster model',
  judge: 'Final response evaluation and refinement using a larger model',
  guardrails: 'Content safety and appropriateness checking'
} as const;

export const CustomPrompts: React.FC = () => {
  const [prompts, setPrompts] = useState<CustomPrompt[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPrompt, setSelectedPrompt] = useState<CustomPrompt | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [preselectedType, setPreselectedType] = useState<'evaluation' | 'judge' | 'guardrails' | null>(null);
  const { toast } = useToast();

  const loadPrompts = async () => {
    try {
      setLoading(true);
      const response = await api.customPrompts.getAll({ active_only: false });
      setPrompts(response.prompts);
    } catch (error) {
      console.error('Failed to load custom prompts:', error);
      toast({
        title: 'Error',
        description: 'Failed to load custom prompts. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPrompts();
  }, []);

  const handleCreate = (promptType?: 'evaluation' | 'judge' | 'guardrails') => {
    setSelectedPrompt(null);
    setIsCreating(true);
    setIsDialogOpen(true);
    // Pass the prompt type if specified (from empty state buttons)
    if (promptType) {
      setPreselectedType(promptType);
    } else {
      setPreselectedType(null);
    }
  };

  const handleEdit = (prompt: CustomPrompt) => {
    setSelectedPrompt(prompt);
    setIsCreating(false);
    setIsDialogOpen(true);
  };

  const handleDelete = async (prompt: CustomPrompt) => {
    if (!confirm(`Are you sure you want to delete "${prompt.name}"?`)) {
      return;
    }

    try {
      await api.customPrompts.delete(prompt.id);
      toast({
        title: 'Success',
        description: 'Custom prompt deleted successfully.',
      });
      loadPrompts();
    } catch (error) {
      console.error('Failed to delete custom prompt:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete custom prompt. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const handleDialogClose = (shouldRefresh?: boolean) => {
    setIsDialogOpen(false);
    setSelectedPrompt(null);
    setIsCreating(false);
    setPreselectedType(null);
    if (shouldRefresh) {
      loadPrompts();
    }
  };

  const groupedPrompts = prompts.reduce((acc, prompt) => {
    if (!acc[prompt.prompt_type]) {
      acc[prompt.prompt_type] = [];
    }
    acc[prompt.prompt_type].push(prompt);
    return acc;
  }, {} as Record<string, CustomPrompt[]>);

  // Get missing prompt types (types that don't have any prompts)
  const allPromptTypes = Object.keys(PROMPT_TYPE_LABELS) as Array<keyof typeof PROMPT_TYPE_LABELS>;
  const missingPromptTypes = allPromptTypes.filter(type => !groupedPrompts[type] || groupedPrompts[type].length === 0);
  const hasAllPromptTypes = missingPromptTypes.length === 0;

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Custom Prompts</h1>
            <p className="text-muted-foreground">
              Manage custom prompts for different AI components
            </p>
          </div>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading custom prompts...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Custom Prompts</h1>
          <p className="text-muted-foreground">
            {hasAllPromptTypes
              ? "All prompt types have been configured. You can edit existing prompts below."
              : "Configure custom prompts for different AI components. Only one prompt per type is allowed."
            }
          </p>
        </div>
        {!hasAllPromptTypes && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              Missing: {missingPromptTypes.map(type => PROMPT_TYPE_LABELS[type]).join(', ')}
            </span>
            <Button onClick={() => handleCreate()} data-testid="create-prompt-button">
              <Plus className="mr-2 h-4 w-4" />
              Create Prompt
            </Button>
          </div>
        )}
      </div>

      <div className="space-y-8">
        {Object.entries(PROMPT_TYPE_LABELS).map(([type, label]) => (
          <div key={type} className="space-y-4">
            <div>
              <h2 className="text-xl font-semibold">{label}</h2>
              <p className="text-sm text-muted-foreground">
                {PROMPT_TYPE_DESCRIPTIONS[type as keyof typeof PROMPT_TYPE_DESCRIPTIONS]}
              </p>
            </div>

            <div className="grid gap-4">
              {groupedPrompts[type] && groupedPrompts[type].length > 0 ? (
                // Show the single prompt for this type
                groupedPrompts[type].slice(0, 1).map((prompt) => (
                  <Card key={prompt.id} className="relative">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <CardTitle className="text-lg">{prompt.name}</CardTitle>
                          <div className="flex items-center gap-2">
                            <Badge variant="default">
                              Active
                            </Badge>
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEdit(prompt)}
                            data-testid={`edit-prompt-${prompt.id}`}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(prompt)}
                            data-testid={`delete-prompt-${prompt.id}`}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      {prompt.description && (
                        <CardDescription className="mb-3">
                          {prompt.description}
                        </CardDescription>
                      )}
                      <div className="text-sm text-muted-foreground">
                        <div>Created: {new Date(prompt.created_at).toLocaleDateString()}</div>
                        <div>Updated: {new Date(prompt.updated_at).toLocaleDateString()}</div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                // Show empty state with create button
                <Card>
                  <CardContent className="flex items-center justify-center h-32">
                    <div className="text-center text-muted-foreground">
                      <p>No {label.toLowerCase()} prompt configured yet.</p>
                      <Button
                        variant="link"
                        onClick={() => handleCreate(type as 'evaluation' | 'judge' | 'guardrails')}
                        className="mt-2"
                        data-testid={`create-${type}-prompt`}
                      >
                        Create {label.toLowerCase()} prompt
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        ))}
      </div>

      <CustomPromptDialog
        open={isDialogOpen}
        onClose={handleDialogClose}
        prompt={selectedPrompt}
        isCreating={isCreating}
        preselectedType={preselectedType}
        availableTypes={missingPromptTypes}
      />
    </div>
  );
};
