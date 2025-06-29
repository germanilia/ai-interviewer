import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Plus,
  Search,
  Edit,
  Trash2,
  Eye,
  MoreHorizontal,
  ChevronLeft,
  ChevronRight,
  Loader2,
  AlertCircle,
  RotateCcw,
  X
} from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { useToast } from '@/hooks/use-toast';
import { useDataLoaders } from '@/hooks/useDataLoaders';
import { api, CandidateResponse, CandidateReportResponse } from '@/lib/api';


interface CandidateFormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  interviewId: string;
}

interface FormErrors {
  firstName?: string;
  lastName?: string;
  email?: string;
  phone?: string;
  interviewId?: string;
}

export const Candidates: React.FC = () => {
  const { toast } = useToast();
  const { interviews, loadInterviews } = useDataLoaders();

  // Helper function to get user-friendly error messages
  const getErrorMessage = (error: any): string => {
    if (error?.message) {
      const message = error.message.toLowerCase();

      // Handle specific error cases
      if (message.includes('email already exists') || message.includes('duplicate')) {
        return 'A candidate with this email already exists';
      }
      if (message.includes('validation') || message.includes('invalid')) {
        return 'Please check your input and try again';
      }
      if (message.includes('not found') || message.includes('404')) {
        return 'Candidate not found';
      }
      if (message.includes('network') || message.includes('timeout')) {
        return 'Network error. Please check your connection and try again';
      }
      if (message.includes('authentication required') || message.includes('unauthorized')) {
        return 'Please log in again to continue';
      }

      // Return the actual error message if it's user-friendly (doesn't contain technical details)
      if (!message.includes('request failed with status') &&
          !message.includes('fetch') &&
          !message.includes('500') &&
          error.message.length < 100) {
        return error.message;
      }
    }
    return 'An unexpected error occurred. Please try again';
  };

  // State management
  const [allCandidates, setAllCandidates] = useState<CandidateResponse[]>([]);
  const [filteredCandidates, setFilteredCandidates] = useState<CandidateResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(0);
  const [totalCandidates, setTotalCandidates] = useState(0);
  const [selectedCandidates, setSelectedCandidates] = useState<Set<number>>(new Set());

  // Modal states
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);

  const [editingCandidate, setEditingCandidate] = useState<CandidateResponse | null>(null);
  const [deletingCandidate, setDeletingCandidate] = useState<CandidateResponse | null>(null);
  const [viewingCandidate, setViewingCandidate] = useState<CandidateResponse | null>(null);
  const [candidateReport, setCandidateReport] = useState<CandidateReportResponse | null>(null);

  const [interviewHistory, setInterviewHistory] = useState<any[]>([]);
  const [loadingInterviewHistory, setLoadingInterviewHistory] = useState(false);

  // Form state
  const [formData, setFormData] = useState<CandidateFormData>({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    interviewId: ''
  });
  const [formErrors, setFormErrors] = useState<FormErrors>({});
  const [submitting, setSubmitting] = useState(false);



  // Fetch candidates data
  const fetchCandidates = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all candidates for client-side filtering
      const response = await api.candidates.getAll({
        page: 1,
        page_size: 1000, // Large page size to get all candidates
        search: searchQuery || undefined,
      });

      setAllCandidates(response.items);
    } catch (err) {
      const errorMessage = getErrorMessage(err);
      setError(errorMessage);
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  }, [searchQuery, toast]);

  // Fetch interview history for a candidate
  const fetchInterviewHistory = useCallback(async (candidateId: number) => {
    try {
      setLoadingInterviewHistory(true);
      const response = await api.candidates.getInterviews(candidateId);
      setInterviewHistory(response.interviews || []);
    } catch (err) {
      const errorMessage = getErrorMessage(err);
      console.error('Error fetching interview history:', errorMessage);
      setInterviewHistory([]);
      toast({
        title: 'Error',
        description: `Failed to load interview history: ${errorMessage}`,
        variant: 'destructive',
      });
    } finally {
      setLoadingInterviewHistory(false);
    }
  }, [toast]);

  // Load candidates and interviews on component mount and when dependencies change
  useEffect(() => {
    fetchCandidates();
    loadInterviews();
  }, [fetchCandidates, loadInterviews]);

  // Debounced search effect
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setCurrentPage(1);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  // Client-side filtering
  useEffect(() => {
    let filtered = [...allCandidates];

    // Apply status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(candidate => {
        const candidateStatus = candidate.interview_status || 'new';
        return candidateStatus === statusFilter;
      });
    }

    setFilteredCandidates(filtered);
    setTotalCandidates(filtered.length);
    setTotalPages(Math.ceil(filtered.length / pageSize));
  }, [allCandidates, statusFilter, pageSize]);

  // Get paginated candidates for display
  const candidates = filteredCandidates.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  // Form validation
  const validateForm = (data: CandidateFormData): FormErrors => {
    const errors: FormErrors = {};

    if (!data.firstName.trim()) {
      errors.firstName = 'First name is required';
    }

    if (!data.lastName.trim()) {
      errors.lastName = 'Last name is required';
    }

    if (!data.email.trim()) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      errors.email = 'Invalid email format';
    }

    if (!data.interviewId.trim()) {
      errors.interviewId = 'Interview assignment is required';
    }

    return errors;
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      interviewId: ''
    });
    setFormErrors({});
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const errors = validateForm(formData);
    setFormErrors(errors);

    if (Object.keys(errors).length > 0) {
      return;
    }

    setSubmitting(true);

    try {
      const requestData = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        phone: formData.phone || undefined,
        interview_id: parseInt(formData.interviewId),
      };

      if (editingCandidate) {
        await api.candidates.update(editingCandidate.id, requestData);
        toast({
          title: 'Success',
          description: 'Candidate updated successfully',
        });
        setShowEditModal(false);
        setEditingCandidate(null);
      } else {
        await api.candidates.create(requestData);
        toast({
          title: 'Success',
          description: 'Candidate created successfully',
        });
        setShowAddModal(false);
      }

      resetForm();
      fetchCandidates();
    } catch (err) {
      const errorMessage = getErrorMessage(err);
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setSubmitting(false);
    }
  };

  // Handle delete candidate
  const handleDelete = async () => {
    if (!deletingCandidate) return;

    setSubmitting(true);

    try {
      await api.candidates.delete(deletingCandidate.id);
      toast({
        title: 'Success',
        description: 'Candidate deleted successfully',
      });
      setShowDeleteModal(false);
      setDeletingCandidate(null);
      fetchCandidates();
    } catch (err) {
      const errorMessage = getErrorMessage(err);
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setSubmitting(false);
    }
  };

  // Handle reset candidate interview
  const handleReset = async (candidate: CandidateResponse) => {
    if (!confirm(`Are you sure you want to reset the interview for ${candidate.first_name} ${candidate.last_name}? This will remove their interview status and date, allowing them to retake the interview.`)) {
      return;
    }

    try {
      await api.candidates.reset(candidate.id);
      toast({
        title: 'Success',
        description: 'Candidate interview reset successfully',
      });
      fetchCandidates();
      // If viewing this candidate, refresh the modal data
      if (viewingCandidate && viewingCandidate.id === candidate.id) {
        const updatedCandidate = await api.candidates.getById(candidate.id);
        setViewingCandidate(updatedCandidate);
      }
    } catch (err) {
      const errorMessage = getErrorMessage(err);
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    }
  };

  // Handle view candidate report
  const handleViewReport = async (candidate: CandidateResponse) => {
    try {
      const report = await api.candidates.getReport(candidate.id);
      if (report) {
        setCandidateReport(report);
        setShowReportModal(true);
      } else {
        toast({
          title: 'No Report Available',
          description: 'No report has been generated for this candidate yet.',
          variant: 'destructive',
        });
      }
    } catch (err) {
      const errorMessage = getErrorMessage(err);
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    }
  };

  // Handle clear search
  const handleClearSearch = () => {
    setSearchQuery('');
    setCurrentPage(1);
  };

  // Handle status filter change
  const handleStatusFilterChange = (value: string) => {
    setStatusFilter(value);
    setCurrentPage(1);
  };

  // Handle page size change
  const handlePageSizeChange = (value: string) => {
    setPageSize(parseInt(value));
    setCurrentPage(1);
  };

  // Handle candidate selection
  const handleSelectCandidate = (candidateId: number, checked: boolean) => {
    const newSelected = new Set(selectedCandidates);
    if (checked) {
      newSelected.add(candidateId);
    } else {
      newSelected.delete(candidateId);
    }
    setSelectedCandidates(newSelected);
  };

  // Handle select all candidates
  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedCandidates(new Set(candidates.map(c => c.id)));
    } else {
      setSelectedCandidates(new Set());
    }
  };

  // Open add modal
  const openAddModal = () => {
    resetForm();
    setShowAddModal(true);
  };

  // Open edit modal
  const openEditModal = (candidate: CandidateResponse) => {
    setFormData({
      firstName: candidate.first_name,
      lastName: candidate.last_name,
      email: candidate.email,
      phone: candidate.phone || '',
      interviewId: candidate.interview_id?.toString() || '',
    });
    setFormErrors({});
    setEditingCandidate(candidate);
    setShowEditModal(true);
  };

  // Open delete modal
  const openDeleteModal = (candidate: CandidateResponse) => {
    setDeletingCandidate(candidate);
    setShowDeleteModal(true);
  };

  // Open detail modal
  const openDetailModal = (candidate: CandidateResponse) => {
    setViewingCandidate(candidate);
    setShowDetailModal(true);
    // Fetch interview history for this candidate
    fetchInterviewHistory(candidate.id);
  };



  // Handle bulk export
  const handleBulkExport = () => {
    const selectedCandidatesList = candidates.filter(candidate =>
      selectedCandidates.has(candidate.id)
    );

    // Create CSV content
    const headers = ['First Name', 'Last Name', 'Email', 'Phone'];
    const csvContent = [
      headers.join(','),
      ...selectedCandidatesList.map(candidate =>
        [candidate.first_name, candidate.last_name, candidate.email, candidate.phone || ''].join(',')
      )
    ].join('\n');

    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `candidates-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);

    toast({
      title: 'Success',
      description: `Exported ${selectedCandidates.size} candidates`,
    });
  };

  // Handle bulk delete
  const handleBulkDelete = async () => {
    if (!confirm(`Are you sure you want to delete ${selectedCandidates.size} candidates? This action cannot be undone.`)) {
      return;
    }

    try {
      const deletePromises = Array.from(selectedCandidates).map(id =>
        api.candidates.delete(id)
      );

      await Promise.all(deletePromises);

      toast({
        title: 'Success',
        description: `Deleted ${selectedCandidates.size} candidates`,
      });

      setSelectedCandidates(new Set());
      fetchCandidates();
    } catch (err) {
      const errorMessage = getErrorMessage(err);
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    }
  };

  // Close all modals
  const closeModals = () => {
    setShowAddModal(false);
    setShowEditModal(false);
    setShowDeleteModal(false);
    setShowDetailModal(false);

    setEditingCandidate(null);
    setDeletingCandidate(null);
    setViewingCandidate(null);
    setInterviewHistory([]);
    setLoadingInterviewHistory(false);
    resetForm();
  };

  // Get status badge variant
  const getStatusVariant = (status?: string) => {
    switch (status) {
      case 'active': return 'default';
      case 'completed': return 'secondary';
      case 'pending': return 'outline';
      case 'new': return 'outline';
      default: return 'outline';
    }
  };

  // Format date
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="space-y-6" data-testid="candidates-section">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground" data-testid="page-title">
            Candidates
          </h1>
          <p className="text-muted-foreground" data-testid="page-subtitle">
            Manage candidate information and interview history
          </p>
        </div>
        <Button
          className="flex items-center gap-2"
          onClick={openAddModal}
          data-testid="add-candidate-btn"
        >
          <Plus className="h-4 w-4" />
          Add Candidate
        </Button>
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-4" data-testid="candidates-toolbar">
        {/* Search */}
        <div className="flex-1" data-testid="search-section">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search candidates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
              data-testid="candidates-search"
            />
            {searchQuery && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-2 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
                onClick={handleClearSearch}
                data-testid="clear-search-btn"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>



        {/* Status Filter */}
        <Select value={statusFilter} onValueChange={handleStatusFilterChange}>
          <SelectTrigger className="w-40" data-testid="status-filter">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="new">New</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
          </SelectContent>
        </Select>

        {/* Refresh Button */}
        <Button
          variant="outline"
          onClick={fetchCandidates}
          disabled={loading}
          data-testid="refresh-candidates-btn"
        >
          <Loader2 className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </Button>
      </div>

      {/* Bulk Actions Bar */}
      {selectedCandidates.size > 0 && (
        <div className="flex items-center justify-between p-4 bg-muted rounded-lg" data-testid="bulk-actions-bar">
          <span className="text-sm font-medium" data-testid="selected-count">
            {selectedCandidates.size} candidate{selectedCandidates.size !== 1 ? 's' : ''} selected
          </span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              data-testid="bulk-export-btn"
              onClick={handleBulkExport}
            >
              Export Selected
            </Button>
            <Button
              variant="destructive"
              size="sm"
              data-testid="bulk-delete-btn"
              onClick={handleBulkDelete}
            >
              Delete Selected
            </Button>
          </div>
        </div>
      )}



      {/* Main Content */}
      <Card data-testid="candidates-list">
        <CardHeader>
          <CardTitle>All Candidates</CardTitle>
          <CardDescription>
            {totalCandidates > 0
              ? `${totalCandidates} candidate${totalCandidates !== 1 ? 's' : ''} found`
              : 'Manage your candidates and their interview history'
            }
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Loading State */}
          {loading && (
            <div className="flex items-center justify-center py-8" data-testid="candidates-loading">
              <Loader2 className="h-8 w-8 animate-spin" />
              <span className="ml-2">Loading candidates...</span>
            </div>
          )}

          {/* Error State */}
          {error && !loading && (
            <div className="flex items-center justify-center py-8 text-destructive" data-testid="error-state">
              <AlertCircle className="h-8 w-8" />
              <span className="ml-2">{error}</span>
            </div>
          )}

          {/* Empty State */}
          {!loading && !error && candidates.length === 0 && (
            <div className="text-center py-8" data-testid="candidates-empty-state">
              <p className="text-muted-foreground mb-4">
                {searchQuery || statusFilter !== 'all'
                  ? 'No candidates match your search criteria.'
                  : 'No candidates found. Add your first candidate to get started.'
                }
              </p>
              {!searchQuery && statusFilter === 'all' && (
                <Button onClick={openAddModal} data-testid="empty-state-add-btn">
                  Add First Candidate
                </Button>
              )}
            </div>
          )}

          {/* Candidates Table */}
          {!loading && !error && candidates.length > 0 && (
            <div className="space-y-4">
              <Table data-testid="candidates-table">
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">
                      <Checkbox
                        checked={selectedCandidates.size === candidates.length && candidates.length > 0}
                        onCheckedChange={handleSelectAll}
                        data-testid="select-all-checkbox"
                      />
                    </TableHead>
                    <TableHead data-testid="name-header">Name</TableHead>
                    <TableHead data-testid="email-header">Email</TableHead>
                    <TableHead data-testid="phone-header">Phone</TableHead>
                    <TableHead data-testid="interview-assignment-header">Interview Assignment</TableHead>
                    <TableHead data-testid="interview-date-header">Interview Date</TableHead>
                    <TableHead data-testid="status-header">Status</TableHead>
                    <TableHead data-testid="actions-header" className="w-12"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {candidates.map((candidate) => (
                    <TableRow key={candidate.id} data-testid="candidate-row">
                      <TableCell>
                        <Checkbox
                          checked={selectedCandidates.has(candidate.id)}
                          onCheckedChange={(checked) => handleSelectCandidate(candidate.id, checked as boolean)}
                          data-testid="candidate-checkbox"
                        />
                      </TableCell>
                      <TableCell>
                        <button
                          onClick={() => openDetailModal(candidate)}
                          className="text-left hover:underline font-medium"
                          data-testid="candidate-name"
                        >
                          {candidate.full_name || `${candidate.first_name} ${candidate.last_name}`}
                        </button>
                      </TableCell>
                      <TableCell data-testid="candidate-email">{candidate.email}</TableCell>
                      <TableCell data-testid="candidate-phone">{candidate.phone || '-'}</TableCell>
                      <TableCell data-testid="candidate-interview">
                        {candidate.interview_id ? (
                          <Badge variant="outline">Assigned</Badge>
                        ) : (
                          <Badge variant="secondary">Unassigned</Badge>
                        )}
                      </TableCell>
                      <TableCell data-testid="candidate-interview-date">{formatDate(candidate.interview_date)}</TableCell>
                      <TableCell data-testid="candidate-status">
                        <Badge variant={getStatusVariant(candidate.interview_status)}>
                          {candidate.interview_status || 'new'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm" className="h-8 w-8 p-0" data-testid="candidate-actions-menu">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => openDetailModal(candidate)}>
                              <Eye className="h-4 w-4 mr-2" />
                              View Details
                            </DropdownMenuItem>

                            <DropdownMenuItem onClick={() => openEditModal(candidate)} data-testid="edit-candidate-btn">
                              <Edit className="h-4 w-4 mr-2" />
                              Edit
                            </DropdownMenuItem>

                            {(candidate.interview_status || candidate.interview_date) && (
                              <DropdownMenuItem
                                onClick={() => handleReset(candidate)}
                                data-testid="reset-candidate-btn"
                                className="text-orange-600"
                              >
                                <RotateCcw className="h-4 w-4 mr-2" />
                                Reset Interview
                              </DropdownMenuItem>
                            )}

                            <DropdownMenuItem
                              onClick={() => openDeleteModal(candidate)}
                              className="text-destructive"
                              data-testid="delete-candidate-btn"
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between" data-testid="pagination-section">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground" data-testid="pagination-info">
                      Showing {((currentPage - 1) * pageSize) + 1}-{Math.min(currentPage * pageSize, totalCandidates)} of {totalCandidates}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <Select value={pageSize.toString()} onValueChange={handlePageSizeChange}>
                      <SelectTrigger className="w-20" data-testid="page-size-select">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="5">5</SelectItem>
                        <SelectItem value="10">10</SelectItem>
                        <SelectItem value="20">20</SelectItem>
                        <SelectItem value="50">50</SelectItem>
                      </SelectContent>
                    </Select>

                    <div className="flex items-center gap-1">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(1)}
                        disabled={currentPage === 1}
                        data-testid="first-page-btn"
                      >
                        First
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(currentPage - 1)}
                        disabled={currentPage === 1}
                        data-testid="prev-page-btn"
                      >
                        <ChevronLeft className="h-4 w-4" />
                      </Button>

                      <span className="px-3 py-1 text-sm">
                        Page {currentPage} of {totalPages}
                      </span>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(currentPage + 1)}
                        disabled={currentPage === totalPages}
                        data-testid="next-page-btn"
                      >
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(totalPages)}
                        disabled={currentPage === totalPages}
                        data-testid="last-page-btn"
                      >
                        Last
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add/Edit Candidate Modal */}
      <Dialog open={showAddModal || showEditModal} onOpenChange={closeModals}>
        <DialogContent className="sm:max-w-md" data-testid={showAddModal ? "add-candidate-modal" : "edit-candidate-modal"}>
          <DialogHeader>
            <DialogTitle data-testid="modal-title">
              {editingCandidate ? 'Edit Candidate' : 'Add New Candidate'}
            </DialogTitle>
            <DialogDescription>
              {editingCandidate
                ? 'Update the candidate information below.'
                : 'Enter the candidate information below.'
              }
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4" data-testid="candidate-form">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName">First Name *</Label>
                <Input
                  id="firstName"
                  value={formData.firstName}
                  onChange={(e) => setFormData(prev => ({ ...prev, firstName: e.target.value }))}
                  placeholder="Enter first name"
                  data-testid="first-name-input"
                />
                {formErrors.firstName && (
                  <p className="text-sm text-destructive" data-testid="first-name-error">
                    {formErrors.firstName}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="lastName">Last Name *</Label>
                <Input
                  id="lastName"
                  value={formData.lastName}
                  onChange={(e) => setFormData(prev => ({ ...prev, lastName: e.target.value }))}
                  placeholder="Enter last name"
                  data-testid="last-name-input"
                />
                {formErrors.lastName && (
                  <p className="text-sm text-destructive" data-testid="last-name-error">
                    {formErrors.lastName}
                  </p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email *</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                placeholder="Enter email address"
                data-testid="email-input"
              />
              {formErrors.email && (
                <p className="text-sm text-destructive" data-testid="email-error">
                  {formErrors.email}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">Phone</Label>
              <Input
                id="phone"
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
                placeholder="Enter phone number"
                data-testid="phone-input"
              />
              {formErrors.phone && (
                <p className="text-sm text-destructive" data-testid="phone-error">
                  {formErrors.phone}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="interview">Interview Assignment *</Label>
              <Select
                value={formData.interviewId}
                onValueChange={(value) => setFormData(prev => ({ ...prev, interviewId: value }))}
              >
                <SelectTrigger data-testid="interview-select">
                  <SelectValue placeholder="Select an interview" />
                </SelectTrigger>
                <SelectContent>
                  {interviews.map((interview) => (
                    <SelectItem
                      key={interview.id}
                      value={interview.id.toString()}
                      data-testid="interview-option"
                    >
                      {interview.job_title} {interview.job_department && `(${interview.job_department})`}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {formErrors.interviewId && (
                <p className="text-sm text-destructive" data-testid="interview-error">
                  {formErrors.interviewId}
                </p>
              )}
            </div>
          </form>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={closeModals}
              data-testid="cancel-btn"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              onClick={handleSubmit}
              disabled={submitting}
              data-testid="save-candidate-btn"
            >
              {submitting && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              {editingCandidate ? 'Update' : 'Create'} Candidate
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Modal */}
      <Dialog open={showDeleteModal} onOpenChange={closeModals}>
        <DialogContent className="sm:max-w-md" data-testid="delete-confirmation-modal">
          <DialogHeader>
            <DialogTitle>Delete Candidate</DialogTitle>
            <DialogDescription data-testid="delete-confirmation-message">
              Are you sure you want to delete {deletingCandidate?.full_name || `${deletingCandidate?.first_name} ${deletingCandidate?.last_name}`}?
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={closeModals}
              data-testid="cancel-delete-btn"
            >
              Cancel
            </Button>
            <Button
              type="button"
              variant="destructive"
              onClick={handleDelete}
              disabled={submitting}
              data-testid="confirm-delete-btn"
            >
              {submitting && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Delete Candidate
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Candidate Detail Modal */}
      <Dialog open={showDetailModal} onOpenChange={closeModals}>
        <DialogContent className="sm:max-w-2xl" data-testid="candidate-detail-view">
          <DialogHeader>
            <DialogTitle>Candidate Details</DialogTitle>
          </DialogHeader>

          {viewingCandidate && (
            <div className="space-y-6">
              {/* Candidate Info */}
              <div className="flex items-start gap-4" data-testid="candidate-info">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center" data-testid="candidate-avatar">
                  <span className="text-xl font-semibold text-primary">
                    {viewingCandidate.first_name[0]}{viewingCandidate.last_name[0]}
                  </span>
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold">
                    {viewingCandidate.full_name || `${viewingCandidate.first_name} ${viewingCandidate.last_name}`}
                  </h3>
                  <p className="text-muted-foreground">{viewingCandidate.email}</p>
                  {viewingCandidate.phone && (
                    <p className="text-muted-foreground">{viewingCandidate.phone}</p>
                  )}
                  <Badge variant={getStatusVariant(viewingCandidate.interview_status)} className="mt-2">
                    {viewingCandidate.interview_status || 'new'}
                  </Badge>
                </div>
              </div>

              {/* Candidate Stats */}
              <div className="grid grid-cols-3 gap-4" data-testid="candidate-stats">
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold">{viewingCandidate.interview_id ? '1' : '0'}</div>
                    <div className="text-sm text-muted-foreground">Interview Assignment</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold">{formatDate(viewingCandidate.interview_date)}</div>
                    <div className="text-sm text-muted-foreground">Interview Date</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold">{formatDate(viewingCandidate.created_at)}</div>
                    <div className="text-sm text-muted-foreground">Added</div>
                  </CardContent>
                </Card>
              </div>

              {/* Pass Key Section */}
              {viewingCandidate.pass_key && (
                <div data-testid="pass-key-section">
                  <h4 className="text-lg font-semibold mb-4">Interview Access</h4>
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Pass Key</p>
                        <code className="text-lg font-mono bg-muted px-2 py-1 rounded">
                          {viewingCandidate.pass_key}
                        </code>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          navigator.clipboard.writeText(viewingCandidate.pass_key || '');
                          toast({
                            title: 'Success',
                            description: 'Pass key copied to clipboard',
                          });
                        }}
                        data-testid="copy-pass-key-btn"
                      >
                        Copy
                      </Button>
                    </div>
                    <p className="text-sm text-muted-foreground mt-2">
                      Share this pass key with the candidate to access their interview.
                    </p>
                  </div>
                </div>
              )}

              {/* Interview History */}
              <div data-testid="interview-history-section">
                <h4 className="text-lg font-semibold mb-4">Interview History</h4>
                <div className="border rounded-lg" data-testid="interview-history-table">
                  {loadingInterviewHistory ? (
                    <div className="p-4 text-center">
                      <Loader2 className="h-4 w-4 animate-spin mx-auto mb-2" />
                      <p className="text-muted-foreground">Loading interview history...</p>
                    </div>
                  ) : interviewHistory.length > 0 ? (
                    <div className="p-0">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Interview</TableHead>
                            <TableHead>Department</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Date</TableHead>
                            <TableHead>Score</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {interviewHistory.map((interview, index) => (
                            <TableRow key={interview.id || index}>
                              <TableCell className="font-medium">
                                {interview.job_title || 'N/A'}
                              </TableCell>
                              <TableCell>
                                {interview.job_department || 'N/A'}
                              </TableCell>
                              <TableCell>
                                <Badge variant={getStatusVariant(interview.interview_status)}>
                                  {interview.interview_status || 'new'}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                {interview.interview_date ? formatDate(interview.interview_date) : 'Not started'}
                              </TableCell>
                              <TableCell>
                                {interview.score ? `${interview.score}/100` : 'N/A'}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  ) : (
                    <div className="p-4 text-center text-muted-foreground">
                      No interviews found for this candidate.
                    </div>
                  )}
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex gap-2">
                <Button onClick={() => openEditModal(viewingCandidate)} data-testid="edit-candidate-button">
                  <Edit className="h-4 w-4 mr-2" />
                  Edit Candidate
                </Button>

                {(viewingCandidate?.interview_status || viewingCandidate?.interview_date) && (
                  <Button
                    variant="outline"
                    onClick={() => viewingCandidate && handleReset(viewingCandidate)}
                    data-testid="reset-candidate-button"
                    className="text-orange-600 border-orange-600 hover:bg-orange-50"
                  >
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Reset Interview
                  </Button>
                )}

                <Button
                  variant="outline"
                  onClick={() => viewingCandidate && handleViewReport(viewingCandidate)}
                  data-testid="view-candidate-report-button"
                >
                  <Eye className="h-4 w-4 mr-2" />
                  View Report
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => openDeleteModal(viewingCandidate)}
                  data-testid="delete-candidate-button"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Candidate Report Modal */}
      <Dialog open={showReportModal} onOpenChange={setShowReportModal}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Candidate Report</DialogTitle>
            <DialogDescription>
              AI-generated assessment report for the candidate
            </DialogDescription>
          </DialogHeader>

          {candidateReport && (
            <div className="space-y-6">
              {/* Header */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-900">{candidateReport.header}</h3>
              </div>

              {/* Overall Assessment */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">Final Grade</h4>
                  <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                    candidateReport.final_grade === 'excellent' ? 'bg-green-100 text-green-800' :
                    candidateReport.final_grade === 'good' ? 'bg-blue-100 text-blue-800' :
                    candidateReport.final_grade === 'satisfactory' ? 'bg-yellow-100 text-yellow-800' :
                    candidateReport.final_grade === 'poor' ? 'bg-orange-100 text-orange-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {candidateReport.final_grade.charAt(0).toUpperCase() + candidateReport.final_grade.slice(1)}
                  </span>
                </div>

                <div className="bg-red-50 p-4 rounded-lg">
                  <h4 className="font-medium text-red-900 mb-2">Risk Level</h4>
                  <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                    candidateReport.overall_risk_level === 'low' ? 'bg-green-100 text-green-800' :
                    candidateReport.overall_risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    candidateReport.overall_risk_level === 'high' ? 'bg-orange-100 text-orange-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {candidateReport.overall_risk_level.charAt(0).toUpperCase() + candidateReport.overall_risk_level.slice(1)} Risk
                  </span>
                </div>
              </div>

              {/* Risk Factors */}
              {candidateReport.risk_factors.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Risk Factors</h4>
                  <div className="space-y-3">
                    {candidateReport.risk_factors.map((factor, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <h5 className="font-medium text-gray-900">{factor.category}</h5>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            factor.severity === 'low' ? 'bg-green-100 text-green-800' :
                            factor.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            factor.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {factor.severity.charAt(0).toUpperCase() + factor.severity.slice(1)}
                          </span>
                        </div>
                        <p className="text-gray-700 mb-2">{factor.description}</p>
                        {factor.evidence && (
                          <div className="bg-gray-50 p-2 rounded text-sm text-gray-600">
                            <strong>Evidence:</strong> {factor.evidence}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* General Observation */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">General Observation</h4>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-700">{candidateReport.general_observation}</p>
                </div>
              </div>

              {/* General Impression */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">General Impression</h4>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-700">{candidateReport.general_impression}</p>
                </div>
              </div>

              {/* Key Strengths and Areas of Concern */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {candidateReport.key_strengths.length > 0 && (
                  <div>
                    <h4 className="font-medium text-green-900 mb-3">Key Strengths</h4>
                    <ul className="space-y-2">
                      {candidateReport.key_strengths.map((strength, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-green-500 mr-2">•</span>
                          <span className="text-gray-700">{strength}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {candidateReport.areas_of_concern.length > 0 && (
                  <div>
                    <h4 className="font-medium text-red-900 mb-3">Areas of Concern</h4>
                    <ul className="space-y-2">
                      {candidateReport.areas_of_concern.map((concern, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-red-500 mr-2">•</span>
                          <span className="text-gray-700">{concern}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Confidence Score */}
              {candidateReport.confidence_score && (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">AI Confidence Score</h4>
                  <div className="flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${candidateReport.confidence_score * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-blue-900">
                      {Math.round(candidateReport.confidence_score * 100)}%
                    </span>
                  </div>
                </div>
              )}

              {/* Report Metadata */}
              <div className="text-sm text-gray-500 border-t pt-4">
                <p>Report generated on: {new Date(candidateReport.created_at).toLocaleDateString()}</p>
                {candidateReport.updated_at !== candidateReport.created_at && (
                  <p>Last updated: {new Date(candidateReport.updated_at).toLocaleDateString()}</p>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

    </div>
  );
};
