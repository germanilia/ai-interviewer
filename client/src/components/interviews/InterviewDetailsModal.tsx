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
import { Copy } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
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
  const { toast } = useToast();

  const handleCopyPassKey = () => {
    if (interview?.pass_key) {
      navigator.clipboard.writeText(interview.pass_key);
      toast({
        title: 'Success',
        description: 'Pass key copied to clipboard',
      });
    }
  };

  if (!interview) return null;

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { label: 'Pending', variant: 'secondary' as const },
      in_progress: { label: 'In Progress', variant: 'default' as const },
      completed: { label: 'Completed', variant: 'success' as const },
      cancelled: { label: 'Cancelled', variant: 'destructive' as const },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || { label: status, variant: 'secondary' as const };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]" data-testid="interview-details-modal">
        <DialogHeader>
          <DialogTitle data-testid="details-modal-title">
            Interview Details
          </DialogTitle>
          <DialogDescription>
            View detailed information about this interview session
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Candidate</h3>
              <p className="text-sm font-medium" data-testid="details-candidate">
                {interview.candidate_name || 
                 interview.candidate?.full_name || 
                 (interview.candidate?.first_name && interview.candidate?.last_name 
                   ? `${interview.candidate.first_name} ${interview.candidate.last_name}` 
                   : 'Unknown')}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Job Position</h3>
              <p className="text-sm font-medium" data-testid="details-job">
                {interview.job_title || interview.job?.title || 'Unknown'}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Status</h3>
              <div data-testid="details-status">
                {getStatusBadge(interview.status)}
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Interview Date</h3>
              <p className="text-sm" data-testid="details-date">
                {interview.interview_date 
                  ? new Date(interview.interview_date).toLocaleString() 
                  : 'Not scheduled'}
              </p>
            </div>
          </div>

          {/* Pass Key */}
          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-2">Pass Key</h3>
            <div className="flex items-center gap-2">
              <code 
                className="bg-muted px-3 py-2 rounded text-sm font-mono flex-1"
                data-testid="details-pass-key"
              >
                {interview.pass_key}
              </code>
              <Button
                variant="outline"
                size="sm"
                onClick={handleCopyPassKey}
                data-testid="copy-pass-key-btn"
              >
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Results (if completed) */}
          {interview.status === 'completed' && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Score</h3>
                <p className="text-sm font-medium" data-testid="details-score">
                  {interview.score ? `${interview.score}%` : 'Not available'}
                </p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Risk Level</h3>
                <div data-testid="details-risk-level">
                  {interview.risk_level ? (
                    <Badge variant={interview.risk_level === 'high' ? 'destructive' : interview.risk_level === 'medium' ? 'secondary' : 'success'}>
                      {interview.risk_level}
                    </Badge>
                  ) : (
                    <span className="text-sm text-muted-foreground">Not available</span>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Timestamps */}
          <div className="grid grid-cols-2 gap-4 text-xs text-muted-foreground">
            <div>
              <h4 className="font-medium">Created</h4>
              <p data-testid="details-created">
                {new Date(interview.created_at).toLocaleString()}
              </p>
            </div>
            <div>
              <h4 className="font-medium">Last Updated</h4>
              <p data-testid="details-updated">
                {new Date(interview.updated_at).toLocaleString()}
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
