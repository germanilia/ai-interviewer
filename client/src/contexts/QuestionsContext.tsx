import React, { createContext, useContext, useState, useCallback } from 'react';
import { api, QuestionResponse, QuestionCreate, QuestionUpdate, QuestionListResponse, QuestionFilter } from '@/lib/api';

interface QuestionsContextType {
  // State
  questions: QuestionResponse[];
  loading: boolean;
  error: string | null;
  totalPages: number;
  currentPage: number;
  pageSize: number;
  total: number;
  filters: QuestionFilter;
  selectedQuestions: Set<number>;

  // Actions
  fetchQuestions: (page?: number, pageSize?: number, filters?: QuestionFilter) => Promise<void>;
  createQuestion: (data: QuestionCreate) => Promise<QuestionResponse>;
  updateQuestion: (id: number, data: QuestionUpdate) => Promise<QuestionResponse>;
  deleteQuestion: (id: number) => Promise<void>;
  bulkDeleteQuestions: (questionIds: number[]) => Promise<void>;
  bulkUpdateCategory: (questionIds: number[], newCategory: QuestionFilter['category']) => Promise<void>;
  assignQuestionToJob: (questionId: number, jobId: number, orderIndex?: number) => Promise<void>;
  searchQuestions: (searchTerm: string, page?: number, pageSize?: number) => Promise<void>;
  filterByCategory: (category: QuestionFilter['category'] | 'all') => Promise<void>;
  
  // Selection management
  selectQuestion: (id: number) => void;
  deselectQuestion: (id: number) => void;
  selectAllQuestions: () => void;
  clearSelection: () => void;
  
  // Utility
  setFilters: (filters: QuestionFilter) => void;
  setPage: (page: number) => void;
  setPageSize: (pageSize: number) => void;
  clearError: () => void;
}

const QuestionsContext = createContext<QuestionsContextType | undefined>(undefined);

export const useQuestions = (): QuestionsContextType => {
  const context = useContext(QuestionsContext);
  if (!context) {
    throw new Error('useQuestions must be used within a QuestionsProvider');
  }
  return context;
};

interface QuestionsProviderProps {
  children: React.ReactNode;
}

export const QuestionsProvider: React.FC<QuestionsProviderProps> = ({ children }) => {
  const [questions, setQuestions] = useState<QuestionResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalPages, setTotalPages] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSizeState] = useState(10);
  const [total, setTotal] = useState(0);
  const [filters, setFiltersState] = useState<QuestionFilter>({});
  const [selectedQuestions, setSelectedQuestions] = useState<Set<number>>(new Set());

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const fetchQuestions = useCallback(async (
    page: number = currentPage,
    size: number = pageSize,
    newFilters: QuestionFilter = filters
  ) => {
    try {
      setLoading(true);
      clearError();

      const response: QuestionListResponse = await api.questions.getAll({
        page,
        page_size: size,
        ...newFilters
      });

      setQuestions(response.questions);
      setTotal(response.total);
      setCurrentPage(response.page);
      setPageSizeState(response.page_size);
      setTotalPages(response.total_pages);
      setFiltersState(newFilters);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch questions';
      setError(errorMessage);
      console.error('Failed to fetch questions:', err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, filters]);

  const createQuestion = useCallback(async (data: QuestionCreate): Promise<QuestionResponse> => {
    try {
      setLoading(true);
      clearError();

      const newQuestion = await api.questions.create(data);
      
      // Refresh the questions list
      await fetchQuestions();
      
      return newQuestion;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create question';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchQuestions]);

  const updateQuestion = useCallback(async (id: number, data: QuestionUpdate): Promise<QuestionResponse> => {
    try {
      setLoading(true);
      clearError();

      const updatedQuestion = await api.questions.update(id, data);
      
      // Update the question in the current list
      setQuestions(prev => prev.map(q => q.id === id ? updatedQuestion : q));
      
      return updatedQuestion;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update question';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteQuestion = useCallback(async (id: number): Promise<void> => {
    try {
      setLoading(true);
      clearError();

      await api.questions.delete(id);
      
      // Remove the question from the current list
      setQuestions(prev => prev.filter(q => q.id !== id));
      setTotal(prev => prev - 1);
      
      // Remove from selection if selected
      setSelectedQuestions(prev => {
        const newSelection = new Set(prev);
        newSelection.delete(id);
        return newSelection;
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete question';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const bulkDeleteQuestions = useCallback(async (questionIds: number[]): Promise<void> => {
    try {
      setLoading(true);
      clearError();

      await api.questions.bulkDelete({ question_ids: questionIds });
      
      // Remove the questions from the current list
      setQuestions(prev => prev.filter(q => !questionIds.includes(q.id)));
      setTotal(prev => prev - questionIds.length);
      
      // Clear selection
      setSelectedQuestions(new Set());
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete questions';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const bulkUpdateCategory = useCallback(async (
    questionIds: number[], 
    newCategory: QuestionFilter['category']
  ): Promise<void> => {
    if (!newCategory) return;
    
    try {
      setLoading(true);
      clearError();

      await api.questions.bulkUpdateCategory({ 
        question_ids: questionIds, 
        new_category: newCategory 
      });
      
      // Update the questions in the current list
      setQuestions(prev => prev.map(q => 
        questionIds.includes(q.id) ? { ...q, category: newCategory } : q
      ));
      
      // Clear selection
      setSelectedQuestions(new Set());
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update question categories';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const assignQuestionToJob = useCallback(async (
    questionId: number, 
    jobId: number, 
    orderIndex?: number
  ): Promise<void> => {
    try {
      setLoading(true);
      clearError();

      await api.questions.assignToJob({ 
        question_id: questionId, 
        job_id: jobId, 
        order_index: orderIndex 
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to assign question to job';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const searchQuestions = useCallback(async (
    searchTerm: string, 
    page: number = 1, 
    size: number = pageSize
  ): Promise<void> => {
    const searchFilters: QuestionFilter = { ...filters, search: searchTerm };
    await fetchQuestions(page, size, searchFilters);
  }, [filters, pageSize, fetchQuestions]);

  const filterByCategory = useCallback(async (
    category: QuestionFilter['category'] | 'all'
  ): Promise<void> => {
    const categoryFilters: QuestionFilter = { 
      ...filters, 
      category: category === 'all' ? undefined : category 
    };
    await fetchQuestions(1, pageSize, categoryFilters);
  }, [filters, pageSize, fetchQuestions]);

  // Selection management
  const selectQuestion = useCallback((id: number) => {
    setSelectedQuestions(prev => new Set(prev).add(id));
  }, []);

  const deselectQuestion = useCallback((id: number) => {
    setSelectedQuestions(prev => {
      const newSelection = new Set(prev);
      newSelection.delete(id);
      return newSelection;
    });
  }, []);

  const selectAllQuestions = useCallback(() => {
    setSelectedQuestions(new Set(questions.map(q => q.id)));
  }, [questions]);

  const clearSelection = useCallback(() => {
    setSelectedQuestions(new Set());
  }, []);

  const setFilters = useCallback((newFilters: QuestionFilter) => {
    setFiltersState(newFilters);
  }, []);

  const setPage = useCallback((page: number) => {
    setCurrentPage(page);
    fetchQuestions(page, pageSize, filters);
  }, [fetchQuestions, pageSize, filters]);

  const setPageSize = useCallback((size: number) => {
    setPageSizeState(size);
  }, []);

  const value: QuestionsContextType = {
    // State
    questions,
    loading,
    error,
    totalPages,
    currentPage,
    pageSize,
    total,
    filters,
    selectedQuestions,

    // Actions
    fetchQuestions,
    createQuestion,
    updateQuestion,
    deleteQuestion,
    bulkDeleteQuestions,
    bulkUpdateCategory,
    assignQuestionToJob,
    searchQuestions,
    filterByCategory,

    // Selection management
    selectQuestion,
    deselectQuestion,
    selectAllQuestions,
    clearSelection,

    // Utility
    setFilters,
    setPage,
    setPageSize,
    clearError,
  };

  return (
    <QuestionsContext.Provider value={value}>
      {children}
    </QuestionsContext.Provider>
  );
};
