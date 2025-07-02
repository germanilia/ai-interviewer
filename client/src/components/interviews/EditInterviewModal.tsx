import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { Search } from 'lucide-react';
import api, { InterviewResponse, QuestionResponse } from '@/lib/api';

interface EditInterviewModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  interview: InterviewResponse | null;
  onInterviewUpdated: () => void;
}

export const EditInterviewModal: React.FC<EditInterviewModalProps> = ({
  open,
  onOpenChange,
  interview,
  onInterviewUpdated,
}) => {
  const [questions, setQuestions] = useState<QuestionResponse[]>([]);
  const [filteredQuestions, setFilteredQuestions] = useState<QuestionResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedQuestions, setSelectedQuestions] = useState<number[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  // Job information fields
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [jobDepartment, setJobDepartment] = useState('');
  const [initialGreeting, setInitialGreeting] = useState('');
  const [instructions, setInstructions] = useState('');

  const { toast } = useToast();

  useEffect(() => {
    if (open && interview) {
      loadQuestions();
      populateForm();
    }
  }, [open, interview]);

  useEffect(() => {
    // Filter questions based on search term
    if (searchTerm.trim()) {
      const filtered = questions.filter(question =>
        question.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        question.question_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
        question.category.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredQuestions(filtered);
    } else {
      setFilteredQuestions(questions);
    }
  }, [searchTerm, questions]);

  const loadQuestions = async () => {
    try {
      const response = await api.questions.getAll({ page_size: 100 });
      setQuestions(response.questions || []);
    } catch (error) {
      console.error('Failed to load questions:', error);
      toast({
        title: 'Error',
        description: 'Failed to load questions',
        variant: 'destructive',
      });
    }
  };

  const populateForm = () => {
    if (!interview) return;

    setJobTitle(interview.job_title || '');
    setJobDescription(interview.job_description || '');
    setJobDepartment(interview.job_department || '');
    setInitialGreeting(interview.initial_greeting || '');
    setInstructions(interview.instructions || '');

    // Set selected questions from interview
    if (interview.questions) {
      setSelectedQuestions(interview.questions.map((q: any) => q.id));
    }
  };

  const handleQuestionToggle = (questionId: number) => {
    setSelectedQuestions(prev =>
      prev.includes(questionId)
        ? prev.filter(id => id !== questionId)
        : [...prev, questionId]
    );
  };

  const handleSelectAllQuestions = () => {
    if (selectedQuestions.length === filteredQuestions.length) {
      setSelectedQuestions([]);
    } else {
      setSelectedQuestions(filteredQuestions.map(q => q.id));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!interview) return;

    if (!jobTitle.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a job title',
        variant: 'destructive',
      });
      return;
    }

    if (selectedQuestions.length === 0) {
      toast({
        title: 'Error',
        description: 'Please select at least one question for the interview',
        variant: 'destructive',
      });
      return;
    }

    try {
      setLoading(true);

      // Update interview basic info
      const interviewData = {
        job_title: jobTitle,
        job_description: jobDescription || undefined,
        job_department: jobDepartment || undefined,
        initial_greeting: initialGreeting || undefined,
        instructions: instructions || undefined,
      };

      await api.interviews.update(interview.id, interviewData);

      // Update interview questions
      await api.interviews.updateQuestions(interview.id, selectedQuestions);

      toast({
        title: 'Success',
        description: 'Interview updated successfully',
      });

      onOpenChange(false);
      onInterviewUpdated();
    } catch (error) {
      console.error('Failed to update interview:', error);
      toast({
        title: 'Error',
        description: 'Failed to update interview',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  if (!interview) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh] flex flex-col" data-testid="edit-interview-modal">
        <DialogHeader className="flex-shrink-0">
          <DialogTitle data-testid="modal-title">
            Edit Interview
          </DialogTitle>
          <DialogDescription>
            Update interview details and modify assigned questions
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-col flex-1 min-h-0">
          <div className="flex-1 overflow-y-auto space-y-6 pr-2">
          {/* Job Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Job Information</h3>
            
            <div className="space-y-2">
              <Label htmlFor="job-title">Job Title *</Label>
              <Input
                id="job-title"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="Enter job title"
                data-testid="job-title-input"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="job-department">Department</Label>
              <Input
                id="job-department"
                value={jobDepartment}
                onChange={(e) => setJobDepartment(e.target.value)}
                placeholder="Enter department (optional)"
                data-testid="job-department-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="job-description">Job Description</Label>
              <Textarea
                id="job-description"
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Enter job description (optional)"
                data-testid="job-description-input"
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="initial-greeting">Initial Greeting Message</Label>
              <Textarea
                id="initial-greeting"
                value={initialGreeting}
                onChange={(e) => setInitialGreeting(e.target.value)}
                placeholder="Hello {candidate_name}, welcome to your interview for {interview_title}..."
                data-testid="initial-greeting-input"
                rows={3}
              />
              <p className="text-sm text-muted-foreground">
                Available variables: {'{candidate_name}'}, {'{interview_title}'}, {'{job_description}'}, {'{job_department}'}
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="instructions">Interview Instructions</Label>
              <Textarea
                id="instructions"
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
                placeholder="Enter special instructions for this interview (optional)"
                data-testid="instructions-input"
                rows={2}
              />
            </div>
          </div>

          {/* Questions Selection */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium">Questions *</h3>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleSelectAllQuestions}
                data-testid="select-all-questions-btn"
              >
                {selectedQuestions.length === filteredQuestions.length ? 'Deselect All' : 'Select All'}
              </Button>
            </div>

            {/* Search Questions */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                placeholder="Search questions by title, content, or category..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
                data-testid="questions-search-input"
              />
            </div>
            
            <div className="max-h-64 overflow-y-auto border rounded-md p-3 space-y-2">
              {filteredQuestions.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  {searchTerm ? 'No questions found matching your search.' : 'No questions available. Please create some questions first.'}
                </p>
              ) : (
                filteredQuestions.map((question) => (
                  <div key={question.id} className="flex items-start space-x-2">
                    <Checkbox
                      id={`question-${question.id}`}
                      checked={selectedQuestions.includes(question.id)}
                      onCheckedChange={() => handleQuestionToggle(question.id)}
                      data-testid={`question-checkbox-${question.id}`}
                    />
                    <Label
                      htmlFor={`question-${question.id}`}
                      className="text-sm leading-relaxed cursor-pointer flex-1"
                    >
                      <div className="font-medium">{question.title}</div>
                      <div className="text-muted-foreground text-xs mt-1">
                        {question.question_text}
                      </div>
                      <div className="flex gap-1 mt-1">
                        <span className="text-xs bg-muted px-1 rounded">{question.category}</span>
                        <span className="text-xs bg-muted px-1 rounded">{question.importance}</span>
                      </div>
                    </Label>
                  </div>
                ))
              )}
            </div>
            
            <p className="text-sm text-muted-foreground">
              {selectedQuestions.length} question{selectedQuestions.length !== 1 ? 's' : ''} selected
            </p>
          </div>
          </div>

          <DialogFooter className="flex-shrink-0 mt-4">
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
              disabled={loading || !jobTitle.trim() || selectedQuestions.length === 0}
              data-testid="save-interview-btn"
            >
              {loading ? 'Updating...' : 'Update Interview'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
