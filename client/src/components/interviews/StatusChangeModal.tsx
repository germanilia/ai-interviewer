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
import { InterviewResponse } from '@/lib/api';
import api from '@/lib/api';

interface StatusChangeModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  interview: InterviewResponse | null;
  onStatusChanged: () => void;
}

const STATUS_OPTIONS = [
  { value: 'pending', label: 'Pending' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
];

export const StatusChangeModal: React.FC<StatusChangeModalProps> = ({
  open,
  onOpenChange,
  interview,
  onStatusChanged,
}) => {
  const [newStatus, setNewStatus] = useState('');
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);

  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!interview || !newStatus) return;

    if (newStatus === interview.status) {
      toast({
        title: 'No Change',
        description: 'The selected status is the same as the current status',
        variant: 'destructive',
      });
      return;
    }

    try {
      setLoading(true);
      await api.interviews.update(interview.id, {
        status: newStatus as any,
        analysis_notes: reason || undefined,
      });
      
      toast({
        title: 'Success',
        description: 'Interview status updated successfully',
      });
      
      onStatusChanged();
      onOpenChange(false);
      resetForm();
    } catch (error) {
      console.error('Failed to update status:', error);
      toast({
        title: 'Error',
        description: 'Failed to update interview status',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setNewStatus('');
    setReason('');
  };

  const handleClose = () => {
    onOpenChange(false);
    resetForm();
  };

  if (!interview) return null;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]" data-testid="status-change-modal">
        <DialogHeader>
          <DialogTitle data-testid="status-modal-title">
            Change Interview Status
          </DialogTitle>
          <DialogDescription>
            Update the status of this interview and provide a reason for the change.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Interview Summary */}
          <div className="p-4 bg-muted rounded-lg space-y-2" data-testid="interview-summary">
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="font-medium">Candidate:</span>
                <div data-testid="candidate-name">
                  {interview.candidate_name || 
                   interview.candidate?.full_name || 
                   'Unknown'}
                </div>
              </div>
              <div>
                <span className="font-medium">Job:</span>
                <div data-testid="job-title">
                  {interview.job_title || interview.job?.title || 'Unknown'}
                </div>
              </div>
              <div>
                <span className="font-medium">Current Status:</span>
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
              <Label htmlFor="new-status">New Status *</Label>
              <Select value={newStatus} onValueChange={setNewStatus}>
                <SelectTrigger data-testid="new-status-select">
                  <SelectValue placeholder="Select new status" />
                </SelectTrigger>
                <SelectContent>
                  {STATUS_OPTIONS.map((option) => (
                    <SelectItem 
                      key={option.value} 
                      value={option.value}
                      disabled={option.value === interview.status}
                      data-testid="status-option"
                    >
                      {option.label}
                      {option.value === interview.status && ' (Current)'}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="reason">Reason for Change (Optional)</Label>
              <Textarea
                id="reason"
                placeholder="Explain why you're changing the status..."
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                data-testid="status-change-reason"
              />
            </div>

            <DialogFooter>
              <Button 
                type="button" 
                variant="outline" 
                onClick={handleClose}
                data-testid="cancel-status-change-btn"
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                disabled={loading || !newStatus || newStatus === interview.status}
                data-testid="confirm-status-change-btn"
              >
                {loading ? 'Updating...' : 'Update Status'}
              </Button>
            </DialogFooter>
          </form>
        </div>
      </DialogContent>
    </Dialog>
  );
};
