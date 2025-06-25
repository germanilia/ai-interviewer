import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { InterviewResponse } from '@/lib/api';

interface InterviewDetailsModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  interview: InterviewResponse | null;
}

export const InterviewDetailsModal: React.FC<InterviewDetailsModalProps> = ({
  open,
  onOpenChange,
  interview,
}) => {
  if (!interview) return null;

  const getCompletionBadge = (completed: number, total: number) => {
    if (total === 0) {
      return <Badge variant="secondary">No Candidates</Badge>;
    }

    const percentage = (completed / total) * 100;
    if (percentage === 100) {
      return <Badge variant="default">Completed</Badge>;
    } else if (percentage > 0) {
      return <Badge variant="outline">In Progress</Badge>;
    } else {
      return <Badge variant="secondary">Pending</Badge>;
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]" data-testid="interview-details-modal">
        <DialogHeader>
          <DialogTitle data-testid="details-modal-title">
            Interview Details
          </DialogTitle>
          <DialogDescription>
            View detailed information about this interview
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Job Information */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Job Title</h3>
              <p className="text-sm font-medium" data-testid="details-job-title">
                {interview.job_title || 'Not specified'}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Department</h3>
              <p className="text-sm font-medium" data-testid="details-job-department">
                {interview.job_department || 'Not specified'}
              </p>
            </div>
          </div>

          {/* Job Description */}
          {interview.job_description && (
            <div>
              <h3 className="text-sm font-medium text-muted-foreground mb-2">Job Description</h3>
              <p className="text-sm bg-muted p-3 rounded" data-testid="details-job-description">
                {interview.job_description}
              </p>
            </div>
          )}

          {/* Candidate Statistics */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Total Candidates</h3>
              <p className="text-lg font-bold" data-testid="details-total-candidates">
                {interview.total_candidates || 0}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Completed</h3>
              <p className="text-lg font-bold" data-testid="details-completed-candidates">
                {interview.completed_candidates || 0}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Progress</h3>
              <div data-testid="details-progress">
                {getCompletionBadge(interview.completed_candidates || 0, interview.total_candidates || 0)}
              </div>
            </div>
          </div>

          {/* Average Score */}
          {interview.avg_score && (
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Average Score</h3>
              <p className="text-lg font-bold" data-testid="details-avg-score">
                {interview.avg_score}%
              </p>
            </div>
          )}

          {/* Questions */}
          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-2">
              Questions ({interview.questions_count || 0})
            </h3>
            {interview.questions && interview.questions.length > 0 ? (
              <div className="space-y-2 max-h-48 overflow-y-auto border rounded p-3">
                {interview.questions.map((question: any) => (
                  <div key={question.id} className="border-b last:border-b-0 pb-2 last:pb-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-medium">{question.title}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {question.question_text}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 ml-2">
                        <Badge variant="outline" className="text-xs">
                          {question.importance}
                        </Badge>
                        <Badge variant="secondary" className="text-xs">
                          {question.category}
                        </Badge>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground bg-muted p-3 rounded">
                No questions assigned to this interview.
              </p>
            )}
          </div>

          {/* Instructions */}
          {interview.instructions && (
            <div>
              <h3 className="text-sm font-medium text-muted-foreground mb-2">Instructions</h3>
              <p className="text-sm bg-muted p-3 rounded" data-testid="details-instructions">
                {interview.instructions}
              </p>
            </div>
          )}

          {/* Timestamps */}
          <div className="grid grid-cols-2 gap-4 text-xs text-muted-foreground">
            <div>
              <h4 className="font-medium">Created</h4>
              <p data-testid="details-created">
                {formatDate(interview.created_at)}
              </p>
            </div>
            <div>
              <h4 className="font-medium">Last Updated</h4>
              <p data-testid="details-updated">
                {formatDate(interview.updated_at)}
              </p>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button
            onClick={() => onOpenChange(false)}
            data-testid="close-details-btn"
          >
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
