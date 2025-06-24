import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { Checkbox } from '@/components/ui/checkbox';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import {
  Plus,
  Search,
  HelpCircle,
  Edit,
  Trash2,
  Eye,
  RefreshCw,
  X,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

import { QuestionsProvider, useQuestions } from '@/contexts/QuestionsContext';
import { QuestionForm } from '@/components/questions/QuestionForm';
import { QuestionPreview } from '@/components/questions/QuestionPreview';
import { QuestionCreate, QuestionUpdate, QuestionResponse } from '@/lib/api';

const QuestionsContent: React.FC = () => {
  const { toast } = useToast();
  const { user } = useAuth();
  const {
    questions,
    loading,
    error,
    totalPages,
    currentPage,
    pageSize,
    total,
    filters,
    selectedQuestions,
    fetchQuestions,
    createQuestion,
    updateQuestion,
    deleteQuestion,
    bulkDeleteQuestions,
    searchQuestions,
    filterByCategory,
    selectQuestion,
    deselectQuestion,
    selectAllQuestions,
    clearSelection,
    setPage,
    clearError
  } = useQuestions();

  // Modal states
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isPreviewModalOpen, setIsPreviewModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isBulkDeleteDialogOpen, setIsBulkDeleteDialogOpen] = useState(false);
  
  // Form states
  const [editingQuestion, setEditingQuestion] = useState<QuestionResponse | null>(null);
  const [previewQuestion, setPreviewQuestion] = useState<QuestionCreate | QuestionUpdate | QuestionResponse | null>(null);
  const [deletingQuestionId, setDeletingQuestionId] = useState<number | null>(null);
  
  // Search and filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategory, setActiveCategory] = useState<'all' | 'criminal_background' | 'drug_use' | 'ethics' | 'dismissals' | 'trustworthiness' | 'general'>('all');

  // Load questions on component mount
  useEffect(() => {
    fetchQuestions();
  }, [fetchQuestions]);

  // Display errors as toasts
  useEffect(() => {
    if (error) {
      toast({
        title: 'Error',
        description: error,
        variant: 'destructive',
      });
      clearError();
    }
  }, [error, toast, clearError]);

  const handleSearch = async (value: string) => {
    setSearchTerm(value);
    if (value.trim()) {
      await searchQuestions(value.trim());
    } else {
      await fetchQuestions();
    }
  };

  const handleCategoryFilter = async (category: string) => {
    const validCategory = category as typeof activeCategory;
    setActiveCategory(validCategory);
    await filterByCategory(validCategory);
  };

  const handleAddQuestion = async (data: QuestionCreate | QuestionUpdate) => {
    try {
      // Ensure user is available
      if (!user?.id) {
        toast({
          title: 'Error',
          description: 'User information not available. Please refresh and try again.',
          variant: 'destructive',
        });
        return;
      }

      // Ensure user ID is included for creation
      const questionData = {
        ...data,
        created_by_user_id: user.id
      } as QuestionCreate;

      await createQuestion(questionData);
      toast({
        title: 'Success',
        description: 'Question created successfully',
        variant: 'default',
      });
      setIsAddModalOpen(false);
    } catch (error) {
      console.error('Failed to create question:', error);
    }
  };

  const handleEditQuestion = (question: QuestionResponse) => {
    setEditingQuestion(question);
    setIsEditModalOpen(true);
  };

  const handleUpdateQuestion = async (data: QuestionCreate | QuestionUpdate) => {
    if (!editingQuestion) return;
    
    try {
      await updateQuestion(editingQuestion.id, data as QuestionUpdate);
      toast({
        title: 'Success',
        description: 'Question updated successfully',
        variant: 'default',
      });
      setIsEditModalOpen(false);
      setEditingQuestion(null);
    } catch (error) {
      console.error('Failed to update question:', error);
    }
  };

  const handleDeleteQuestion = (questionId: number) => {
    setDeletingQuestionId(questionId);
    setIsDeleteDialogOpen(true);
  };

  const confirmDeleteQuestion = async () => {
    if (!deletingQuestionId) return;
    
    try {
      await deleteQuestion(deletingQuestionId);
      toast({
        title: 'Success',
        description: 'Question deleted successfully',
        variant: 'default',
      });
      setIsDeleteDialogOpen(false);
      setDeletingQuestionId(null);
    } catch (error) {
      console.error('Failed to delete question:', error);
    }
  };

  const handleBulkDelete = () => {
    if (selectedQuestions.size === 0) return;
    setIsBulkDeleteDialogOpen(true);
  };

  const confirmBulkDelete = async () => {
    try {
      await bulkDeleteQuestions(Array.from(selectedQuestions));
      toast({
        title: 'Success',
        description: `Successfully deleted ${selectedQuestions.size} questions`,
        variant: 'default',
      });
      setIsBulkDeleteDialogOpen(false);
    } catch (error) {
      console.error('Failed to bulk delete questions:', error);
    }
  };

  const handlePreviewQuestion = (question: QuestionResponse) => {
    setPreviewQuestion(question);
    setIsPreviewModalOpen(true);
  };

  const handlePreviewFromForm = (data: QuestionCreate | QuestionUpdate) => {
    setPreviewQuestion(data);
    setIsPreviewModalOpen(true);
  };

  const handleQuestionSelect = (questionId: number, checked: boolean) => {
    if (checked) {
      selectQuestion(questionId);
    } else {
      deselectQuestion(questionId);
    }
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      selectAllQuestions();
    } else {
      clearSelection();
    }
  };

  const getCategoryLabel = (category: string): string => {
    const categoryLabels: Record<string, string> = {
      criminal_background: 'Criminal Background',
      drug_use: 'Drug Use',
      ethics: 'Ethics',
      dismissals: 'Dismissals',
      trustworthiness: 'Trustworthiness',
      general: 'General',
    };
    return categoryLabels[category] || category;
  };

  const getImportanceLabel = (importance: string): string => {
    const importanceLabels: Record<string, string> = {
      optional: 'Optional',
      ask_once: 'Ask Once',
      mandatory: 'Mandatory',
    };
    return importanceLabels[importance] || importance;
  };

  return (
    <div className="space-y-6" data-testid="questions-section">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground" data-testid="page-title">
            Questions
          </h1>
          <p className="text-muted-foreground" data-testid="page-subtitle">
            Manage interview questions and question bank
          </p>
        </div>
        <div className="flex gap-2" data-testid="questions-toolbar">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchQuestions()}
            data-testid="refresh-questions-btn"
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button
            onClick={() => setIsAddModalOpen(true)}
            data-testid="add-question-btn"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Question
          </Button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="flex items-center gap-4" data-testid="search-section">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search questions..."
            className="pl-10 pr-20"
            data-testid="questions-search"
          />
          {searchTerm && (
            <Button
              variant="ghost"
              size="sm"
              className="absolute right-16 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
              onClick={() => handleSearch('')}
              data-testid="clear-search-btn"
            >
              <X className="h-3 w-3" />
            </Button>
          )}
        </div>
        <Button
          onClick={() => handleSearch(searchTerm)}
          data-testid="search-btn"
        >
          <Search className="h-4 w-4 mr-2" />
          Search
        </Button>
      </div>

      {/* Category Tabs */}
      <Tabs value={activeCategory} onValueChange={handleCategoryFilter} className="w-full" data-testid="category-tabs">
        <TabsList className="grid w-full grid-cols-7">
          <TabsTrigger value="all" data-testid="all-categories-tab">All</TabsTrigger>
          <TabsTrigger value="criminal_background" data-testid="criminal-background-tab">Criminal</TabsTrigger>
          <TabsTrigger value="drug_use" data-testid="drug-use-tab">Drug Use</TabsTrigger>
          <TabsTrigger value="ethics" data-testid="ethics-tab">Ethics</TabsTrigger>
          <TabsTrigger value="dismissals" data-testid="dismissals-tab">Dismissals</TabsTrigger>
          <TabsTrigger value="trustworthiness" data-testid="trustworthiness-tab">Trust</TabsTrigger>
          <TabsTrigger value="general" data-testid="general-tab">General</TabsTrigger>
        </TabsList>

        {/* Questions Table */}
        <TabsContent value={activeCategory} className="space-y-4">
          {/* Bulk Actions Bar */}
          {selectedQuestions.size > 0 && (
            <div 
              className="flex items-center justify-between p-4 bg-muted rounded-lg"
              data-testid="bulk-actions-bar"
            >
              <span data-testid="selected-count">
                {selectedQuestions.size} question{selectedQuestions.size !== 1 ? 's' : ''} selected
              </span>
              <div className="flex gap-2">
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleBulkDelete}
                  data-testid="bulk-delete-btn"
                >
                  Delete Selected
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearSelection}
                >
                  Clear Selection
                </Button>
              </div>
            </div>
          )}

          <Card data-testid="questions-list">
            <CardHeader>
              <CardTitle>Questions</CardTitle>
              <CardDescription>
                {activeCategory === 'all' 
                  ? 'All questions in the question bank' 
                  : `Questions in the ${getCategoryLabel(activeCategory)} category`
                }
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8" data-testid="questions-loading">
                  <p className="text-muted-foreground">Loading questions...</p>
                </div>
              ) : questions.length === 0 ? (
                <div className="text-center py-8" data-testid="questions-empty-state">
                  <HelpCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">
                    {searchTerm 
                      ? `No questions found matching "${searchTerm}"` 
                      : 'No questions found. Add your first question to get started.'
                    }
                  </p>
                  {!searchTerm && (
                    <Button 
                      className="mt-4" 
                      onClick={() => setIsAddModalOpen(true)}
                      data-testid="empty-state-add-btn"
                    >
                      Add First Question
                    </Button>
                  )}
                </div>
              ) : (
                <Table data-testid="questions-table">
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">
                        <Checkbox
                          checked={selectedQuestions.size === questions.length && questions.length > 0}
                          onCheckedChange={handleSelectAll}
                          data-testid="select-all-checkbox"
                        />
                      </TableHead>
                      <TableHead data-testid="title-header">Title</TableHead>
                      <TableHead data-testid="category-header">Category</TableHead>
                      <TableHead data-testid="importance-header">Importance</TableHead>
                      <TableHead data-testid="created-by-header">Created By</TableHead>
                      <TableHead data-testid="created-date-header">Created</TableHead>
                      <TableHead data-testid="actions-header">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {questions.map((question) => (
                      <TableRow key={question.id} data-testid="question-row">
                        <TableCell>
                          <Checkbox
                            checked={selectedQuestions.has(question.id)}
                            onCheckedChange={(checked) => handleQuestionSelect(question.id, Boolean(checked))}
                            data-testid="question-checkbox"
                          />
                        </TableCell>
                        <TableCell>
                          <div className="max-w-xs">
                            <p 
                              className="font-medium truncate" 
                              data-testid="question-title"
                              title={question.title}
                            >
                              {question.title}
                            </p>
                            <p 
                              className="text-sm text-muted-foreground truncate" 
                              title={question.question_text}
                            >
                              {question.question_text}
                            </p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" data-testid="question-category">
                            {getCategoryLabel(question.category)}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant={question.importance === 'mandatory' ? 'destructive' : 'secondary'}
                            data-testid="question-importance"
                          >
                            {getImportanceLabel(question.importance)}
                          </Badge>
                        </TableCell>
                        <TableCell data-testid="question-created-by">
                          {question.created_by_name || 'Unknown'}
                        </TableCell>
                        <TableCell data-testid="question-created-date">
                          {new Date(question.created_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handlePreviewQuestion(question)}
                              data-testid="preview-question-btn"
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEditQuestion(question)}
                              data-testid="edit-question-btn"
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteQuestion(question.id)}
                              data-testid="delete-question-btn"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between" data-testid="pagination-controls">
              <div className="text-sm text-muted-foreground">
                Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, total)} of {total} questions
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(currentPage - 1)}
                  disabled={currentPage <= 1}
                  data-testid="prev-page-btn"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </Button>
                <div className="flex items-center gap-1">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                    <Button
                      key={page}
                      variant={page === currentPage ? "default" : "outline"}
                      size="sm"
                      onClick={() => setPage(page)}
                      data-testid={`page-${page}-btn`}
                      className="min-w-[40px]"
                    >
                      {page}
                    </Button>
                  ))}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(currentPage + 1)}
                  disabled={currentPage >= totalPages}
                  data-testid="next-page-btn"
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Questions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="total-questions-count">{total}</div>
            <p className="text-xs text-muted-foreground">All categories</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Selected</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{selectedQuestions.size}</div>
            <p className="text-xs text-muted-foreground">Questions selected</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Categories</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">6</div>
            <p className="text-xs text-muted-foreground">Available</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Current Page</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{currentPage}</div>
            <p className="text-xs text-muted-foreground">of {totalPages} pages</p>
          </CardContent>
        </Card>
      </div>

      {/* Modals */}
      <QuestionForm
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSubmit={handleAddQuestion}
        mode="create"
        onPreview={handlePreviewFromForm}
      />

      <QuestionForm
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setEditingQuestion(null);
        }}
        onSubmit={handleUpdateQuestion}
        initialData={editingQuestion || undefined}
        mode="edit"
        onPreview={handlePreviewFromForm}
      />

      {previewQuestion && (
        <QuestionPreview
          isOpen={isPreviewModalOpen}
          onClose={() => {
            setIsPreviewModalOpen(false);
            setPreviewQuestion(null);
          }}
          question={previewQuestion}
        />
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent data-testid="delete-confirmation-modal">
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Question</AlertDialogTitle>
            <AlertDialogDescription data-testid="delete-confirmation-message">
              Are you sure you want to delete this question? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel data-testid="cancel-delete-btn">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction 
              onClick={confirmDeleteQuestion}
              data-testid="confirm-delete-btn"
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Bulk Delete Confirmation Dialog */}
      <AlertDialog open={isBulkDeleteDialogOpen} onOpenChange={setIsBulkDeleteDialogOpen}>
        <AlertDialogContent data-testid="bulk-delete-confirmation-modal">
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Multiple Questions</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete{' '}
              <span data-testid="bulk-delete-count">{selectedQuestions.size}</span>{' '}
              questions? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={confirmBulkDelete}
              data-testid="confirm-bulk-delete-btn"
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete {selectedQuestions.size} Questions
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>


    </div>
  );
};

export const Questions: React.FC = () => {
  return (
    <QuestionsProvider>
      <QuestionsContent />
    </QuestionsProvider>
  );
};
