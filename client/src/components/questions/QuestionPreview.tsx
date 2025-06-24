import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { QuestionCreate, QuestionUpdate, QuestionResponse } from '@/lib/api';
import { X } from 'lucide-react';

interface QuestionPreviewProps {
  isOpen: boolean;
  onClose: () => void;
  question: QuestionCreate | QuestionUpdate | QuestionResponse;
}

const getCategoryLabel = (category: string): string => {
  const categoryLabels: Record<string, string> = {
    criminal_background: 'Criminal Background',
    drug_use: 'Drug Use',
    ethics: 'Ethics',
    dismissals: 'Dismissals',
    trustworthiness: 'Trustworthiness',
    general: 'General',
  };
  return categoryLabels[category] || category;
};

const getImportanceLabel = (importance: string): string => {
  const importanceLabels: Record<string, string> = {
    optional: 'Optional',
    ask_once: 'Ask Once',
    mandatory: 'Mandatory',
  };
  return importanceLabels[importance] || importance;
};

const getCategoryVariant = (category: string) => {
  const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
    criminal_background: 'destructive',
    drug_use: 'secondary',
    ethics: 'default',
    dismissals: 'outline',
    trustworthiness: 'secondary',
    general: 'outline',
  };
  return variants[category] || 'outline';
};

const getImportanceVariant = (importance: string) => {
  const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
    optional: 'outline',
    ask_once: 'secondary',
    mandatory: 'destructive',
  };
  return variants[importance] || 'outline';
};

export const QuestionPreview: React.FC<QuestionPreviewProps> = ({
  isOpen,
  onClose,
  question
}) => {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent 
        className="max-w-3xl max-h-[90vh] overflow-y-auto"
        data-testid="preview-modal"
      >
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle>Question Preview</DialogTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              data-testid="close-preview-btn"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <DialogDescription>
            Preview how this question will appear during interviews
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Question Header */}
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <CardTitle 
                    className="text-xl font-semibold text-foreground" 
                    data-testid="preview-title"
                  >
                    {question.title}
                  </CardTitle>
                </div>
                <div className="flex gap-2">
                  <Badge 
                    variant={getCategoryVariant(question.category || '')}
                    data-testid="preview-category"
                  >
                    {getCategoryLabel(question.category || '')}
                  </Badge>
                  <Badge 
                    variant={getImportanceVariant(question.importance || '')}
                    data-testid="preview-importance"
                  >
                    {getImportanceLabel(question.importance || '')}
                  </Badge>
                </div>
              </div>
            </CardHeader>
          </Card>

          {/* Question Content */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Interview Question</CardTitle>
            </CardHeader>
            <CardContent>
              <div 
                className="text-foreground whitespace-pre-wrap leading-relaxed"
                data-testid="preview-question-text"
              >
                {question.question_text}
              </div>
            </CardContent>
          </Card>

          {/* Instructions (if provided) */}
          {question.instructions && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Instructions for Interviewer</CardTitle>
              </CardHeader>
              <CardContent>
                <div 
                  className="text-muted-foreground whitespace-pre-wrap leading-relaxed"
                  data-testid="preview-instructions"
                >
                  {question.instructions}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Question Metadata */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Question Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-sm text-muted-foreground">Category</h4>
                  <p className="text-foreground" data-testid="preview-category">
                    {getCategoryLabel(question.category || '')}
                  </p>
                </div>
                <div>
                  <h4 className="font-medium text-sm text-muted-foreground">Importance</h4>
                  <p className="text-foreground" data-testid="preview-importance">
                    {getImportanceLabel(question.importance || '')}
                  </p>
                </div>
                <div>
                  <h4 className="font-medium text-sm text-muted-foreground">Character Count</h4>
                  <p className="text-foreground">
                    {question.question_text?.length || 0} characters
                  </p>
                </div>
                <div>
                  <h4 className="font-medium text-sm text-muted-foreground">Instructions</h4>
                  <p className="text-foreground">
                    {question.instructions ? 'Provided' : 'None'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Interview Simulation */}
          <Card className="border-primary/20">
            <CardHeader>
              <CardTitle className="text-base text-primary">Interview Simulation</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground mb-2">
                  <strong>Interviewer:</strong>
                </p>
                <p className="text-foreground">{question.question_text}</p>
              </div>
              
              {question.instructions && (
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-xs text-blue-600 mb-1">
                    <strong>Internal Instructions:</strong>
                  </p>
                  <p className="text-sm text-blue-800">{question.instructions}</p>
                </div>
              )}

              <div className="p-4 bg-background border border-dashed border-muted-foreground rounded-lg">
                <p className="text-sm text-muted-foreground mb-2">
                  <strong>Candidate Response:</strong>
                </p>
                <p className="text-muted-foreground italic">
                  [Candidate's answer will appear here during the interview]
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
};
