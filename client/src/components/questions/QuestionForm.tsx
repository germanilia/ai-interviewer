import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { QuestionCreate, QuestionUpdate, QuestionResponse } from '@/lib/api';

interface QuestionFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: QuestionCreate | QuestionUpdate) => Promise<void>;
  initialData?: QuestionResponse;
  mode: 'create' | 'edit';
  onPreview?: (data: QuestionCreate | QuestionUpdate) => void;
}

const IMPORTANCE_OPTIONS = [
  { value: 'optional', label: 'Optional' },
  { value: 'ask_once', label: 'Ask Once' },
  { value: 'mandatory', label: 'Mandatory' },
];

const CATEGORY_OPTIONS = [
  { value: 'criminal_background', label: 'Criminal Background' },
  { value: 'drug_use', label: 'Drug Use' },
  { value: 'ethics', label: 'Ethics' },
  { value: 'dismissals', label: 'Dismissals' },
  { value: 'trustworthiness', label: 'Trustworthiness' },
  { value: 'general', label: 'General' },
];

export const QuestionForm: React.FC<QuestionFormProps> = ({
  isOpen,
  onClose,
  onSubmit,
  initialData,
  mode,
  onPreview
}) => {
  const [formData, setFormData] = useState<QuestionCreate>({
    title: '',
    question_text: '',
    instructions: '',
    importance: 'optional',
    category: 'general',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      if (mode === 'edit' && initialData) {
        setFormData({
          title: initialData.title,
          question_text: initialData.question_text,
          instructions: initialData.instructions || '',
          importance: initialData.importance,
          category: initialData.category,
        });
      } else {
        setFormData({
          title: '',
          question_text: '',
          instructions: '',
          importance: 'optional',
          category: 'general',
        });
      }
      setErrors({});
    }
  }, [isOpen, mode, initialData]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }

    if (!formData.question_text.trim()) {
      newErrors.question_text = 'Question text is required';
    } else if (formData.question_text.trim().length < 20) {
      newErrors.question_text = 'Question text must be at least 20 characters long';
    }

    if (!formData.importance) {
      newErrors.importance = 'Importance is required';
    }

    if (!formData.category) {
      newErrors.category = 'Category is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      onClose();
    } catch (error) {
      console.error('Failed to submit question:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePreview = () => {
    if (onPreview && validateForm()) {
      onPreview(formData);
    }
  };

  const handleInputChange = (field: keyof QuestionCreate, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent 
        className="max-w-2xl max-h-[90vh] overflow-y-auto"
        data-testid={mode === 'create' ? 'add-question-modal' : 'edit-question-modal'}
      >
        <DialogHeader>
          <DialogTitle data-testid="modal-title">
            {mode === 'create' ? 'Add New Question' : 'Edit Question'}
          </DialogTitle>
          <DialogDescription>
            {mode === 'create' 
              ? 'Create a new question for the question bank.' 
              : 'Update the question details.'
            }
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} data-testid="question-form">
          <div className="space-y-4">
            {/* Title */}
            <div className="space-y-2">
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="Enter question title"
                data-testid="title-input"
              />
              {errors.title && (
                <p className="text-sm text-destructive" data-testid="title-error">
                  {errors.title}
                </p>
              )}
            </div>

            {/* Question Text */}
            <div className="space-y-2">
              <Label htmlFor="question_text">Question Text *</Label>
              <Textarea
                id="question_text"
                value={formData.question_text}
                onChange={(e) => handleInputChange('question_text', e.target.value)}
                placeholder="Enter the interview question (minimum 20 characters)"
                rows={4}
                data-testid="question-text-area"
              />
              <p className="text-xs text-muted-foreground">
                {formData.question_text.length}/2000 characters (minimum 20)
              </p>
              {errors.question_text && (
                <p className="text-sm text-destructive" data-testid="question-text-error">
                  {errors.question_text}
                </p>
              )}
            </div>

            {/* Instructions */}
            <div className="space-y-2">
              <Label htmlFor="instructions">Instructions (Optional)</Label>
              <Textarea
                id="instructions"
                value={formData.instructions}
                onChange={(e) => handleInputChange('instructions', e.target.value)}
                placeholder="Additional instructions for the interviewer"
                rows={3}
                data-testid="instructions-text-area"
              />
              <p className="text-xs text-muted-foreground">
                {formData.instructions?.length || 0}/1000 characters
              </p>
            </div>

            {/* Importance */}
            <div className="space-y-2">
              <Label htmlFor="importance">Importance *</Label>
              <Select
                value={formData.importance}
                onValueChange={(value) => handleInputChange('importance', value)}
                data-testid="importance-select"
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select importance level" />
                </SelectTrigger>
                <SelectContent>
                  {IMPORTANCE_OPTIONS.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.importance && (
                <p className="text-sm text-destructive" data-testid="importance-error">
                  {errors.importance}
                </p>
              )}
            </div>

            {/* Category */}
            <div className="space-y-2">
              <Label htmlFor="category">Category *</Label>
              <Select
                value={formData.category}
                onValueChange={(value) => handleInputChange('category', value)}
                data-testid="category-select"
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {CATEGORY_OPTIONS.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.category && (
                <p className="text-sm text-destructive" data-testid="category-error">
                  {errors.category}
                </p>
              )}
            </div>
          </div>

          <DialogFooter className="mt-6">
            <div className="flex gap-2">
              {onPreview && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={handlePreview}
                  data-testid="preview-question-btn"
                >
                  Preview
                </Button>
              )}
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                data-testid="cancel-btn"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isSubmitting}
                data-testid="save-question-btn"
              >
                {isSubmitting ? 'Saving...' : (mode === 'create' ? 'Create Question' : 'Update Question')}
              </Button>
            </div>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
