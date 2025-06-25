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
import { useToast } from '@/hooks/use-toast';
import { Checkbox } from '@/components/ui/checkbox';
import { Search } from 'lucide-react';
import api, { InterviewResponse, QuestionResponse } from '@/lib/api';

interface CreateInterviewModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onInterviewCreated: () => void;
}

export const CreateInterviewModal: React.FC<CreateInterviewModalProps> = ({
  open,
  onOpenChange,
  onInterviewCreated,
}) => {
  const [questions, setQuestions] = useState<QuestionResponse[]>([]);
  const [filteredQuestions, setFilteredQuestions] = useState<QuestionResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedQuestions, setSelectedQuestions] = useState<number[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  // Job information fields (now part of interview)
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [jobDepartment, setJobDepartment] = useState('');
  const [instructions, setInstructions] = useState('');
  const [createdInterview, setCreatedInterview] = useState<InterviewResponse | null>(null);
  const [step, setStep] = useState<'form' | 'success'>('form');

  const { toast } = useToast();

  useEffect(() => {
    if (open) {
      loadQuestions();
      resetForm();
    }
  }, [open]);

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

  const resetForm = () => {
    setSelectedQuestions([]);
    setJobTitle('');
    setJobDescription('');
    setJobDepartment('');
    setInstructions('');
    setCreatedInterview(null);
    setStep('form');
    setSearchTerm('');
  };

  const handleQuestionToggle = (questionId: number) => {
    setSelectedQuestions(prev =>
      prev.includes(questionId)
        ? prev.filter(id => id !== questionId)
        : [...prev, questionId]
    );
  };

  const handleSelectAllQuestions = () => {
    const filteredIds = filteredQuestions.map(q => q.id);
    const allFilteredSelected = filteredIds.every(id => selectedQuestions.includes(id));

    if (allFilteredSelected) {
      // Deselect all filtered questions
      setSelectedQuestions(prev => prev.filter(id => !filteredIds.includes(id)));
    } else {
      // Select all filtered questions
      setSelectedQuestions(prev => [...new Set([...prev, ...filteredIds])]);
    }
  };

  const handleClose = () => {
    onOpenChange(false);
    if (step === 'success') {
      onInterviewCreated();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

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
      const interviewData = {
        job_title: jobTitle,
        job_description: jobDescription || undefined,
        job_department: jobDepartment || undefined,
        instructions: instructions || undefined,
        question_ids: selectedQuestions,
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
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Job Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Job Information</h3>

              <div className="space-y-2">
                <Label htmlFor="job-title">Job Title *</Label>
                <Input
                  id="job-title"
                  placeholder="e.g. Software Engineer"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  data-testid="job-title-input"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="job-department">Department</Label>
                <Input
                  id="job-department"
                  placeholder="e.g. Engineering"
                  value={jobDepartment}
                  onChange={(e) => setJobDepartment(e.target.value)}
                  data-testid="job-department-input"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="job-description">Job Description</Label>
                <Textarea
                  id="job-description"
                  placeholder="Describe the role and responsibilities..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  data-testid="job-description-input"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="instructions">Interview Instructions</Label>
                <Textarea
                  id="instructions"
                  placeholder="Special instructions for this interview..."
                  value={instructions}
                  onChange={(e) => setInstructions(e.target.value)}
                  data-testid="instructions-input"
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
                  {filteredQuestions.length > 0 && filteredQuestions.every(q => selectedQuestions.includes(q.id)) ? 'Deselect All' : 'Select All'}
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
                disabled={loading || !jobTitle.trim() || selectedQuestions.length === 0}
                data-testid="save-interview-btn"
              >
                {loading ? 'Creating...' : 'Create Interview'}
              </Button>
            </DialogFooter>
          </form>
        ) : (
          <div className="space-y-6">
            <div className="text-center space-y-4" data-testid="interview-created-display">
              <div className="p-6 bg-muted rounded-lg">
                <h3 className="text-lg font-semibold mb-2">Interview Created Successfully</h3>
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    Job Title: <span className="font-medium">{createdInterview?.job_title}</span>
                  </p>
                  {createdInterview?.job_department && (
                    <p className="text-sm text-muted-foreground">
                      Department: <span className="font-medium">{createdInterview.job_department}</span>
                    </p>
                  )}
                  <p className="text-sm text-muted-foreground">
                    Questions: <span className="font-medium">{selectedQuestions.length} selected</span>
                  </p>
                </div>
              </div>

              <div className="text-sm text-muted-foreground" data-testid="next-steps">
                <p>Your interview is ready! You can now:</p>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>Assign candidates to this interview</li>
                  <li>View and manage the interview from the interviews page</li>
                </ul>
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
