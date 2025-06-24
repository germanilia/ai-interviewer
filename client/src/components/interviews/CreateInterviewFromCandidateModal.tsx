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
import { useToast } from '@/hooks/use-toast';
import { Copy } from 'lucide-react';
import api, { CandidateResponse, JobResponse, InterviewResponse } from '@/lib/api';

interface CreateInterviewFromCandidateModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  candidate: CandidateResponse | null;
  onInterviewCreated: () => void;
  jobs?: JobResponse[];
  loading?: boolean;
}

export const CreateInterviewFromCandidateModal: React.FC<CreateInterviewFromCandidateModalProps> = ({
  open,
  onOpenChange,
  candidate,
  onInterviewCreated,
  jobs: preloadedJobs = [],
  loading: dataLoading = false,
}) => {
  const [jobs, setJobs] = useState<JobResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedJob, setSelectedJob] = useState<string>('');
  const [notes, setNotes] = useState('');
  const [scheduledDate, setScheduledDate] = useState('');
  const [createdInterview, setCreatedInterview] = useState<InterviewResponse | null>(null);
  const [step, setStep] = useState<'form' | 'success'>('form');

  const { toast } = useToast();

  useEffect(() => {
    if (open) {
      // Use preloaded data if available, otherwise load from API
      if (preloadedJobs.length > 0) {
        setJobs(preloadedJobs);
      } else {
        loadJobs();
      }
      resetForm();
    }
  }, [open, preloadedJobs]);

  const loadJobs = async () => {
    try {
      const response = await api.jobs.getAll({ page_size: 100 });
      setJobs(response.jobs || []);
    } catch (error) {
      console.error('Failed to load jobs:', error);
      toast({
        title: 'Error',
        description: 'Failed to load jobs',
        variant: 'destructive',
      });
    }
  };

  const resetForm = () => {
    setSelectedJob('');
    setNotes('');
    setScheduledDate('');
    setCreatedInterview(null);
    setStep('form');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!candidate || !selectedJob) {
      toast({
        title: 'Error',
        description: 'Please select a job position',
        variant: 'destructive',
      });
      return;
    }

    try {
      setLoading(true);
      const interviewData = {
        candidate_id: candidate.id,
        job_id: parseInt(selectedJob),
        notes: notes || undefined,
        interview_date: scheduledDate || undefined,
      };

      const interview = await api.interviews.create(interviewData);
      setCreatedInterview(interview);
      setStep('success');
      
      toast({
        title: 'Success',
        description: 'Interview created successfully',
      });
    } catch (error) {
      console.error('Failed to create interview:', error);
      toast({
        title: 'Error',
        description: 'Failed to create interview',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCopyPassKey = () => {
    if (createdInterview?.pass_key) {
      navigator.clipboard.writeText(createdInterview.pass_key);
      toast({
        title: 'Success',
        description: 'Pass key copied to clipboard',
      });
    }
  };

  const handleClose = () => {
    if (step === 'success') {
      onInterviewCreated();
    }
    onOpenChange(false);
  };

  if (!candidate) return null;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]" data-testid="create-interview-from-candidate-modal">
        <DialogHeader>
          <DialogTitle data-testid="modal-title">
            {step === 'form' ? 'Create Interview' : 'Interview Created Successfully'}
          </DialogTitle>
          <DialogDescription>
            {step === 'form' 
              ? `Set up a new interview session for ${candidate.full_name || `${candidate.first_name} ${candidate.last_name}`}`
              : 'Your interview has been created with an auto-generated pass key'
            }
          </DialogDescription>
        </DialogHeader>

        {step === 'form' ? (
          <div className="space-y-4">
            {(dataLoading || jobs.length === 0) ? (
              <div className="flex items-center justify-center py-8" data-testid="loading-state">
                <div className="text-center space-y-2">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                  <p className="text-sm text-muted-foreground">Loading job positions...</p>
                </div>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Candidate Info (Read-only) */}
                <div className="p-4 bg-muted rounded-lg">
                  <h3 className="text-sm font-medium mb-2">Selected Candidate</h3>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                      <span className="text-sm font-semibold text-primary">
                        {candidate.first_name[0]}{candidate.last_name[0]}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium" data-testid="selected-candidate-name">
                        {candidate.full_name || `${candidate.first_name} ${candidate.last_name}`}
                      </p>
                      <p className="text-sm text-muted-foreground" data-testid="selected-candidate-email">
                        {candidate.email}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="job">Job Position *</Label>
                  <Select value={selectedJob} onValueChange={setSelectedJob}>
                    <SelectTrigger data-testid="job-select">
                      <SelectValue placeholder="Select a job position" />
                    </SelectTrigger>
                    <SelectContent>
                      {jobs.map((job) => (
                        <SelectItem
                          key={job.id}
                          value={job.id.toString()}
                          data-testid="job-option"
                        >
                          {job.title} {job.department && `(${job.department})`}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

            <div className="space-y-2">
              <Label htmlFor="scheduled-date">Scheduled Date (Optional)</Label>
              <Input
                id="scheduled-date"
                type="datetime-local"
                value={scheduledDate}
                onChange={(e) => setScheduledDate(e.target.value)}
                data-testid="scheduled-date-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Notes (Optional)</Label>
              <Textarea
                id="notes"
                placeholder="Add any notes about this interview..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                data-testid="notes-input"
              />
            </div>

                <DialogFooter>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => onOpenChange(false)}
                    data-testid="cancel-btn"
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={loading || !selectedJob}
                    data-testid="save-interview-btn"
                  >
                    {loading ? 'Creating...' : 'Create Interview'}
                  </Button>
                </DialogFooter>
              </form>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            <div className="text-center space-y-4" data-testid="pass-key-display">
              <div className="p-6 bg-muted rounded-lg">
                <h3 className="text-lg font-semibold mb-2">Interview Pass Key</h3>
                <div className="flex items-center justify-center gap-2">
                  <code 
                    className="text-2xl font-mono bg-background px-4 py-2 rounded border"
                    data-testid="pass-key-value"
                  >
                    {createdInterview?.pass_key}
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
              
              <div className="text-sm text-muted-foreground" data-testid="pass-key-instructions">
                <p>Share this pass key with {candidate.first_name} to start their interview.</p>
                <p>The candidate will use this key to access the interview session.</p>
              </div>
            </div>

            <DialogFooter>
              <Button onClick={handleClose} data-testid="modal-close-btn">
                Done
              </Button>
            </DialogFooter>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};
