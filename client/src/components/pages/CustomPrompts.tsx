import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Power, PowerOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { api, CustomPrompt } from '@/lib/api';
import { CustomPromptDialog } from '@/components/dialogs/CustomPromptDialog';

const PROMPT_TYPE_LABELS = {
  small_llm: 'Small LLM',
  judge: 'Judge',
  guardrails: 'Guardrails'
} as const;

const PROMPT_TYPE_DESCRIPTIONS = {
  small_llm: 'Initial response generation using a smaller, faster model',
  judge: 'Final response evaluation and refinement using a larger model',
  guardrails: 'Content safety and appropriateness checking'
} as const;

export const CustomPrompts: React.FC = () => {
  const [prompts, setPrompts] = useState<CustomPrompt[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPrompt, setSelectedPrompt] = useState<CustomPrompt | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
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

  const handleCreate = () => {
    setSelectedPrompt(null);
    setIsCreating(true);
    setIsDialogOpen(true);
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

  const handleToggleActive = async (prompt: CustomPrompt) => {
    try {
      if (prompt.is_active) {
        // Deactivate by updating the prompt
        await api.customPrompts.update(prompt.id, { is_active: false });
      } else {
        // Activate and deactivate others of the same type
        await api.customPrompts.activate(prompt.id, true);
      }
      
      toast({
        title: 'Success',
        description: `Custom prompt ${prompt.is_active ? 'deactivated' : 'activated'} successfully.`,
      });
      loadPrompts();
    } catch (error) {
      console.error('Failed to toggle prompt status:', error);
      toast({
        title: 'Error',
        description: 'Failed to update prompt status. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const handleDialogClose = (shouldRefresh?: boolean) => {
    setIsDialogOpen(false);
    setSelectedPrompt(null);
    setIsCreating(false);
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
            Manage custom prompts for different AI components
          </p>
        </div>
        <Button onClick={handleCreate} data-testid="create-prompt-button">
          <Plus className="mr-2 h-4 w-4" />
          Create Prompt
        </Button>
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

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {groupedPrompts[type]?.map((prompt) => (
                <Card key={prompt.id} className="relative">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <CardTitle className="text-lg">{prompt.name}</CardTitle>
                        <div className="flex items-center gap-2">
                          <Badge variant={prompt.is_active ? 'default' : 'secondary'}>
                            {prompt.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleToggleActive(prompt)}
                          data-testid={`toggle-prompt-${prompt.id}`}
                        >
                          {prompt.is_active ? (
                            <PowerOff className="h-4 w-4" />
                          ) : (
                            <Power className="h-4 w-4" />
                          )}
                        </Button>
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
              )) || (
                <Card className="col-span-full">
                  <CardContent className="flex items-center justify-center h-32">
                    <div className="text-center text-muted-foreground">
                      <p>No {label.toLowerCase()} prompts created yet.</p>
                      <Button
                        variant="link"
                        onClick={handleCreate}
                        className="mt-2"
                        data-testid={`create-${type}-prompt`}
                      >
                        Create your first {label.toLowerCase()} prompt
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
      />
    </div>
  );
};
