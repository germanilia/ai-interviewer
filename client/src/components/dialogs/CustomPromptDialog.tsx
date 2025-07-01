import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { api, CustomPrompt, CustomPromptCreate, CustomPromptUpdate } from '@/lib/api';
import { PromptType, PROMPT_TYPES } from '@/types/prompts';

const promptSchema = z.object({
  prompt_type: z.enum([
    PROMPT_TYPES.EVALUATION,
    PROMPT_TYPES.JUDGE,
    PROMPT_TYPES.GUARDRAILS,
    PROMPT_TYPES.QUESTION_EVALUATION
  ], {
    required_error: 'Please select a prompt type',
  }),
  name: z.string().min(1, 'Name is required').max(100, 'Name must be less than 100 characters'),
  content: z.string().min(10, 'Content must be at least 10 characters'),
  description: z.string().optional(),
});

type FormData = z.infer<typeof promptSchema>;

import { PROMPT_TYPE_OPTIONS } from '@/types/prompts';

interface CustomPromptDialogProps {
  open: boolean;
  onClose: (shouldRefresh?: boolean) => void;
  prompt?: CustomPrompt | null;
  isCreating: boolean;
  preselectedType?: PromptType | null;
  availableTypes?: string[];
}

export const CustomPromptDialog: React.FC<CustomPromptDialogProps> = ({
  open,
  onClose,
  prompt,
  isCreating,
  preselectedType,
  availableTypes = [],
}) => {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const { user } = useAuth();

  const form = useForm<FormData>({
    resolver: zodResolver(promptSchema),
    defaultValues: {
      prompt_type: preselectedType || (availableTypes.length > 0 ? availableTypes[0] as PromptType : PROMPT_TYPES.EVALUATION),
      name: '',
      content: '',
      description: '',
    },
  });

  useEffect(() => {
    if (open) {
      if (prompt && !isCreating) {
        // Editing existing prompt
        form.reset({
          prompt_type: prompt.prompt_type,
          name: prompt.name,
          content: prompt.content,
          description: prompt.description || '',
        });
      } else {
        // Creating new prompt
        const defaultType = preselectedType || (availableTypes.length > 0 ? availableTypes[0] as PromptType : PROMPT_TYPES.EVALUATION);
        form.reset({
          prompt_type: defaultType,
          name: '',
          content: '',
          description: '',
        });
      }
    }
  }, [open, prompt, isCreating, form]);

  const onSubmit = async (data: FormData) => {
    if (!user) {
      toast({
        title: 'Error',
        description: 'You must be logged in to perform this action.',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    try {
      if (isCreating) {
        const createData: CustomPromptCreate = {
          ...data,
          is_active: true, // Always active since only one per type
          created_by_user_id: user.id,
        };
        await api.customPrompts.create(createData);
        toast({
          title: 'Success',
          description: 'Custom prompt created successfully.',
        });
      } else if (prompt) {
        const updateData: CustomPromptUpdate = {
          name: data.name,
          content: data.content,
          description: data.description,
          is_active: true, // Always active since only one per type
        };
        await api.customPrompts.update(prompt.id, updateData);
        toast({
          title: 'Success',
          description: 'Custom prompt updated successfully.',
        });
      }
      onClose(true); // Refresh the list
    } catch (error) {
      console.error('Failed to save custom prompt:', error);
      toast({
        title: 'Error',
        description: `Failed to ${isCreating ? 'create' : 'update'} custom prompt. Please try again.`,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    form.reset();
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {isCreating ? 'Create Custom Prompt' : 'Edit Custom Prompt'}
          </DialogTitle>
          <DialogDescription>
            {isCreating
              ? 'Create a custom prompt for an AI component. Only one prompt per type is allowed.'
              : 'Edit the selected custom prompt. This will replace the current prompt for this type.'}
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="prompt_type"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Prompt Type</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                    disabled={!isCreating} // Don't allow changing type when editing
                  >
                    <FormControl>
                      <SelectTrigger data-testid="prompt-type-select">
                        <SelectValue placeholder="Select a prompt type" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {PROMPT_TYPE_OPTIONS
                        .filter(option =>
                          !isCreating || // Show all when editing
                          availableTypes.length === 0 || // Show all if no restrictions
                          availableTypes.includes(option.value) // Show only available types when creating
                        )
                        .map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            <div>
                              <div className="font-medium">{option.label}</div>
                              <div className="text-sm text-muted-foreground">
                                {option.description}
                              </div>
                            </div>
                          </SelectItem>
                        ))}
                    </SelectContent>
                  </Select>
                  <FormDescription>
                    The type of AI component this prompt will be used for.
                    {!isCreating && ' (Cannot be changed when editing)'}
                    {isCreating && availableTypes.length > 0 && ` Only missing types are available: ${availableTypes.join(', ')}.`}
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Enter prompt name"
                      {...field}
                      data-testid="prompt-name-input"
                    />
                  </FormControl>
                  <FormDescription>
                    A descriptive name for this custom prompt.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description (Optional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Enter prompt description"
                      className="min-h-[80px]"
                      {...field}
                      data-testid="prompt-description-input"
                    />
                  </FormControl>
                  <FormDescription>
                    Optional description explaining what this prompt does.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="content"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Prompt Content</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Enter the prompt content..."
                      className="min-h-[200px] font-mono text-sm"
                      {...field}
                      data-testid="prompt-content-input"
                    />
                  </FormControl>
                  <FormDescription>
                    The actual prompt content. You can use variables like {'{candidate_name}'}, {'{interview_title}'}, etc.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="rounded-lg border p-4 bg-muted/50">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-green-500"></div>
                <span className="text-sm font-medium">Auto-Active</span>
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                This prompt will be automatically active since only one prompt per type is allowed.
              </p>
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={handleClose}
                disabled={loading}
                data-testid="cancel-button"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={loading}
                data-testid="save-button"
              >
                {loading ? 'Saving...' : isCreating ? 'Create' : 'Update'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};
