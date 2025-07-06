import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { CreateInterviewModal } from '../CreateInterviewModal';
import api from '@/lib/api';

// Mock the API
jest.mock('@/lib/api');
const mockApi = api as jest.Mocked<typeof api>;

// Mock the ReorderableQuestionList component
jest.mock('../ReorderableQuestionList', () => ({
  ReorderableQuestionList: ({ selectedQuestionIds, onReorder, onRemove }: any) => (
    <div data-testid="reorderable-question-list">
      <div data-testid="selected-questions">{selectedQuestionIds.join(',')}</div>
      <button 
        data-testid="mock-reorder-btn" 
        onClick={() => onReorder([3, 1, 2])}
      >
        Reorder
      </button>
      <button 
        data-testid="mock-remove-btn" 
        onClick={() => onRemove(1)}
      >
        Remove
      </button>
    </div>
  ),
}));

// Mock the toast hook
jest.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}));

const mockQuestions = [
  {
    id: 1,
    title: 'Question 1',
    question_text: 'First question',
    importance: 'mandatory',
    category: 'criminal_background',
    created_by_user_id: 1,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
  },
  {
    id: 2,
    title: 'Question 2',
    question_text: 'Second question',
    importance: 'ask_once',
    category: 'ethics',
    created_by_user_id: 1,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
  },
  {
    id: 3,
    title: 'Question 3',
    question_text: 'Third question',
    importance: 'optional',
    category: 'general',
    created_by_user_id: 1,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
  },
];

describe('CreateInterviewModal - Question Reordering', () => {
  const mockOnInterviewCreated = jest.fn();
  const mockOnOpenChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockApi.questions.getAll.mockResolvedValue({
      questions: mockQuestions,
      total: 3,
      page: 1,
      page_size: 10,
      total_pages: 1,
    });
  });

  it('shows question selection tab by default', async () => {
    render(
      <CreateInterviewModal
        open={true}
        onOpenChange={mockOnOpenChange}
        onInterviewCreated={mockOnInterviewCreated}
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId('select-questions-tab')).toBeInTheDocument();
      expect(screen.getByTestId('reorder-questions-tab')).toBeInTheDocument();
    });

    // Select tab should be active by default
    expect(screen.getByTestId('select-questions-tab')).toHaveAttribute('data-state', 'active');
    expect(screen.getByTestId('reorder-questions-tab')).toHaveAttribute('data-state', 'inactive');
  });

  it('disables reorder tab when no questions are selected', async () => {
    render(
      <CreateInterviewModal
        open={true}
        onOpenChange={mockOnOpenChange}
        onInterviewCreated={mockOnInterviewCreated}
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId('reorder-questions-tab')).toBeDisabled();
    });
  });

  it('enables reorder tab when questions are selected', async () => {
    render(
      <CreateInterviewModal
        open={true}
        onOpenChange={mockOnOpenChange}
        onInterviewCreated={mockOnInterviewCreated}
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId('question-checkbox-1')).toBeInTheDocument();
    });

    // Select a question
    fireEvent.click(screen.getByTestId('question-checkbox-1'));

    await waitFor(() => {
      expect(screen.getByTestId('reorder-questions-tab')).not.toBeDisabled();
    });
  });

  it('shows continue to reorder button when questions are selected', async () => {
    render(
      <CreateInterviewModal
        open={true}
        onOpenChange={mockOnOpenChange}
        onInterviewCreated={mockOnInterviewCreated}
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId('question-checkbox-1')).toBeInTheDocument();
    });

    // Select a question
    fireEvent.click(screen.getByTestId('question-checkbox-1'));

    await waitFor(() => {
      expect(screen.getByTestId('continue-to-reorder-btn')).toBeInTheDocument();
    });
  });

  it('switches to reorder tab when continue button is clicked', async () => {
    render(
      <CreateInterviewModal
        open={true}
        onOpenChange={mockOnOpenChange}
        onInterviewCreated={mockOnInterviewCreated}
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId('question-checkbox-1')).toBeInTheDocument();
    });

    // Select questions
    fireEvent.click(screen.getByTestId('question-checkbox-1'));
    fireEvent.click(screen.getByTestId('question-checkbox-2'));

    // Click continue to reorder
    fireEvent.click(screen.getByTestId('continue-to-reorder-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('reorder-questions-tab')).toHaveAttribute('data-state', 'active');
      expect(screen.getByTestId('reorderable-question-list')).toBeInTheDocument();
    });
  });

  it('shows back to selection button in reorder tab', async () => {
    render(
      <CreateInterviewModal
        open={true}
        onOpenChange={mockOnOpenChange}
        onInterviewCreated={mockOnInterviewCreated}
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId('question-checkbox-1')).toBeInTheDocument();
    });

    // Select a question and go to reorder
    fireEvent.click(screen.getByTestId('question-checkbox-1'));
    fireEvent.click(screen.getByTestId('continue-to-reorder-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('back-to-selection-btn')).toBeInTheDocument();
    });
  });

  it('creates interview with questions in correct order', async () => {
    const mockCreatedInterview = {
      id: 1,
      job_title: 'Test Job',
      language: 'Hebrew',
      total_candidates: 0,
      completed_candidates: 0,
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z',
    };

    mockApi.interviews.create.mockResolvedValue(mockCreatedInterview);

    render(
      <CreateInterviewModal
        open={true}
        onOpenChange={mockOnOpenChange}
        onInterviewCreated={mockOnInterviewCreated}
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId('question-checkbox-1')).toBeInTheDocument();
    });

    // Fill in job title
    fireEvent.change(screen.getByTestId('job-title-input'), {
      target: { value: 'Test Job' },
    });

    // Select questions in order 1, 2, 3
    fireEvent.click(screen.getByTestId('question-checkbox-1'));
    fireEvent.click(screen.getByTestId('question-checkbox-2'));
    fireEvent.click(screen.getByTestId('question-checkbox-3'));

    // Go to reorder tab
    fireEvent.click(screen.getByTestId('continue-to-reorder-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('reorderable-question-list')).toBeInTheDocument();
    });

    // Reorder questions to 3, 1, 2
    fireEvent.click(screen.getByTestId('mock-reorder-btn'));

    // Go back to selection and submit
    fireEvent.click(screen.getByTestId('back-to-selection-btn'));
    fireEvent.click(screen.getByTestId('save-interview-btn'));

    await waitFor(() => {
      expect(mockApi.interviews.create).toHaveBeenCalledWith({
        job_title: 'Test Job',
        language: 'Hebrew',
        question_ids: [3, 1, 2], // Reordered
      });
    });
  });

  it('handles question removal from reorder list', async () => {
    render(
      <CreateInterviewModal
        open={true}
        onOpenChange={mockOnOpenChange}
        onInterviewCreated={mockOnInterviewCreated}
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId('question-checkbox-1')).toBeInTheDocument();
    });

    // Select questions
    fireEvent.click(screen.getByTestId('question-checkbox-1'));
    fireEvent.click(screen.getByTestId('question-checkbox-2'));

    // Go to reorder tab
    fireEvent.click(screen.getByTestId('continue-to-reorder-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('selected-questions')).toHaveTextContent('1,2');
    });

    // Remove a question
    fireEvent.click(screen.getByTestId('mock-remove-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('selected-questions')).toHaveTextContent('2');
    });
  });
});
