import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { AlertTriangle } from 'lucide-react';
import api, { InterviewResponse } from '@/lib/api';

interface CancelInterviewModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  interview: InterviewResponse | null;
  onInterviewCancelled: () => void;
}

const CANCELLATION_REASONS = [
  'Candidate requested cancellation',
  'Technical difficulties',
  'Scheduling conflict',
  'Position filled',
  'Candidate no longer interested',
  'Internal decision',
  'Other',
];

export const CancelInterviewModal: React.FC<CancelInterviewModalProps> = ({
  open,
  onOpenChange,
  interview,
  onInterviewCancelled,
}) => {
  const [reason, setReason] = useState('');
  const [customReason, setCustomReason] = useState('');
  const [loading, setLoading] = useState(false);

  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!interview) return;

    const finalReason = reason === 'Other' ? customReason : reason;
    
    if (!finalReason.trim()) {
      toast({
        title: 'Error',
        description: 'Please provide a reason for cancellation',
        variant: 'destructive',
      });
      return;
    }

    try {
      setLoading(true);
      await api.interviews.cancel(interview.id, finalReason);
      
      toast({
        title: 'Success',
        description: 'Interview cancelled successfully',
      });
      
      onInterviewCancelled();
      onOpenChange(false);
      resetForm();
    } catch (error) {
      console.error('Failed to cancel interview:', error);
      toast({
        title: 'Error',
        description: 'Failed to cancel interview',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setReason('');
    setCustomReason('');
  };

  const handleClose = () => {
    onOpenChange(false);
    resetForm();
  };

  if (!interview) return null;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]" data-testid="cancel-interview-modal">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2" data-testid="cancel-modal-title">
            <AlertTriangle className="h-5 w-5 text-orange-500" />
            Cancel Interview
          </DialogTitle>
          <DialogDescription>
            Are you sure you want to cancel this interview? This action cannot be undone.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Interview Details */}
          <div className="p-4 bg-muted rounded-lg space-y-2" data-testid="interview-summary">
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="font-medium">Candidate:</span>
                <div data-testid="candidate-name">
                  {interview.candidate?.full_name || 'Unknown'}
                </div>
              </div>
              <div>
                <span className="font-medium">Job:</span>
                <div data-testid="job-title">
                  {interview.job?.title || 'Unknown'}
                </div>
              </div>
              <div>
                <span className="font-medium">Status:</span>
                <div data-testid="current-status">
                  {interview.status.replace('_', ' ').toUpperCase()}
                </div>
              </div>
              <div>
                <span className="font-medium">Pass Key:</span>
                <code className="text-xs bg-background px-2 py-1 rounded" data-testid="pass-key">
                  {interview.pass_key}
                </code>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="reason">Reason for Cancellation *</Label>
              <Select value={reason} onValueChange={setReason}>
                <SelectTrigger data-testid="cancellation-reason-select">
                  <SelectValue placeholder="Select a reason" />
                </SelectTrigger>
                <SelectContent>
                  {CANCELLATION_REASONS.map((reasonOption) => (
                    <SelectItem 
                      key={reasonOption} 
                      value={reasonOption}
                      data-testid="reason-option"
                    >
                      {reasonOption}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {reason === 'Other' && (
              <div className="space-y-2">
                <Label htmlFor="custom-reason">Custom Reason *</Label>
                <Textarea
                  id="custom-reason"
                  placeholder="Please specify the reason for cancellation..."
                  value={customReason}
                  onChange={(e) => setCustomReason(e.target.value)}
                  data-testid="custom-reason-input"
                />
              </div>
            )}

            {reason && reason !== 'Other' && (
              <div className="space-y-2">
                <Label htmlFor="additional-notes">Additional Notes (Optional)</Label>
                <Textarea
                  id="additional-notes"
                  placeholder="Add any additional context..."
                  value={customReason}
                  onChange={(e) => setCustomReason(e.target.value)}
                  data-testid="additional-notes-input"
                />
              </div>
            )}

            <DialogFooter>
              <Button 
                type="button" 
                variant="outline" 
                onClick={handleClose}
                data-testid="cancel-btn"
              >
                Keep Interview
              </Button>
              <Button 
                type="submit" 
                variant="destructive"
                disabled={loading || !reason || (reason === 'Other' && !customReason.trim())}
                data-testid="confirm-cancel-btn"
              >
                {loading ? 'Cancelling...' : 'Cancel Interview'}
              </Button>
            </DialogFooter>
          </form>
        </div>
      </DialogContent>
    </Dialog>
  );
};
