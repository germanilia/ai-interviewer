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
import { Copy, Check } from 'lucide-react';
import api, { CandidateResponse, JobResponse, InterviewResponse } from '@/lib/api';

interface CreateInterviewModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onInterviewCreated: () => void;
  candidates?: any[];
  jobs?: any[];
  loading?: boolean;
}

export const CreateInterviewModal: React.FC<CreateInterviewModalProps> = ({
  open,
  onOpenChange,
  onInterviewCreated,
  candidates: preloadedCandidates = [],
  jobs: preloadedJobs = [],
  loading: dataLoading = false,
}) => {
  const [candidates, setCandidates] = useState<CandidateResponse[]>([]);
  const [jobs, setJobs] = useState<JobResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [candidateSearch, setCandidateSearch] = useState('');
  const [selectedCandidate, setSelectedCandidate] = useState<string>('');
  const [selectedJob, setSelectedJob] = useState<string>('');
  const [notes, setNotes] = useState('');
  const [scheduledDate, setScheduledDate] = useState('');
  const [createdInterview, setCreatedInterview] = useState<InterviewResponse | null>(null);
  const [step, setStep] = useState<'form' | 'success'>('form');

  const { toast } = useToast();

  useEffect(() => {
    if (open) {
      // Use preloaded data if available, otherwise load from API
      if (preloadedCandidates.length > 0) {
        setCandidates(preloadedCandidates);
      } else {
        loadCandidates();
      }

      if (preloadedJobs.length > 0) {
        setJobs(preloadedJobs);
      } else {
        loadJobs();
      }

      resetForm();
    }
  }, [open, preloadedCandidates, preloadedJobs]);

  const loadCandidates = async () => {
    try {
      const response = await api.candidates.getAll({ page_size: 100 });
      setCandidates(response.items || []);
    } catch (error) {
      console.error('Failed to load candidates:', error);
      toast({
        title: 'Error',
        description: 'Failed to load candidates',
        variant: 'destructive',
      });
    }
  };

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
    setSelectedCandidate('');
    setSelectedJob('');
    setNotes('');
    setScheduledDate('');
    setCandidateSearch('');
    setCreatedInterview(null);
    setStep('form');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedCandidate || !selectedJob) {
      toast({
        title: 'Error',
        description: 'Please select both a candidate and a job',
        variant: 'destructive',
      });
      return;
    }

    try {
      setLoading(true);
      const interviewData = {
        candidate_id: parseInt(selectedCandidate),
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

  const filteredCandidates = candidates.filter(candidate =>
    candidateSearch === '' ||
    `${candidate.first_name} ${candidate.last_name}`.toLowerCase().includes(candidateSearch.toLowerCase()) ||
    candidate.email.toLowerCase().includes(candidateSearch.toLowerCase())
  );

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]" data-testid="create-interview-modal">
        <DialogHeader>
          <DialogTitle data-testid="modal-title">
            {step === 'form' ? 'Create New Interview' : 'Interview Created Successfully'}
          </DialogTitle>
          <DialogDescription>
            {step === 'form' 
              ? 'Set up a new interview session for a candidate'
              : 'Your interview has been created with an auto-generated pass key'
            }
          </DialogDescription>
        </DialogHeader>

        {step === 'form' ? (
          <div className="space-y-4">
            {(dataLoading || (candidates.length === 0 && jobs.length === 0)) ? (
              <div className="flex items-center justify-center py-8" data-testid="loading-state">
                <div className="text-center space-y-2">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                  <p className="text-sm text-muted-foreground">Loading candidates and jobs...</p>
                </div>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="candidate">Candidate *</Label>
                  <div className="space-y-2">
                    <Input
                      placeholder="Search candidates..."
                      value={candidateSearch}
                      onChange={(e) => setCandidateSearch(e.target.value)}
                      data-testid="candidate-search-input"
                    />
                    <Select value={selectedCandidate} onValueChange={setSelectedCandidate}>
                      <SelectTrigger data-testid="candidate-select">
                        <SelectValue placeholder="Select a candidate" />
                      </SelectTrigger>
                      <SelectContent>
                        {filteredCandidates.map((candidate) => (
                          <SelectItem
                            key={candidate.id}
                            value={candidate.id.toString()}
                            data-testid="candidate-option"
                          >
                            {candidate.first_name} {candidate.last_name} ({candidate.email})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
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
                    disabled={loading || !selectedCandidate || !selectedJob}
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
                <p>Share this pass key with the candidate to start their interview.</p>
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
