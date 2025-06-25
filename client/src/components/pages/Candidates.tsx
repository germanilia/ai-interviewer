import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Plus,
  Search,
  Filter,
  Edit,
  Trash2,
  Eye,
  MoreHorizontal,
  ChevronLeft,
  ChevronRight,
  Loader2,
  AlertCircle,

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
import { api, CandidateResponse } from '@/lib/api';


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
  const [candidates, setCandidates] = useState<CandidateResponse[]>([]);
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

  const [editingCandidate, setEditingCandidate] = useState<CandidateResponse | null>(null);
  const [deletingCandidate, setDeletingCandidate] = useState<CandidateResponse | null>(null);
  const [viewingCandidate, setViewingCandidate] = useState<CandidateResponse | null>(null);
  const [showFilters, setShowFilters] = useState(false);

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

      const response = await api.candidates.getAll({
        page: currentPage,
        page_size: pageSize,
        search: searchQuery || undefined,
        status: statusFilter !== 'all' ? statusFilter : undefined,
      });

      setCandidates(response.items);
      setTotalCandidates(response.total);
      setTotalPages(response.total_pages);
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
  }, [currentPage, pageSize, searchQuery, statusFilter, toast]);

  // Load candidates and interviews on component mount and when dependencies change
  useEffect(() => {
    fetchCandidates();
    loadInterviews();
  }, [fetchCandidates, loadInterviews]);

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

  // Handle search
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchCandidates();
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
        <form onSubmit={handleSearch} className="flex-1" data-testid="search-section">
          <div className="flex gap-2">
            <div className="relative flex-1">
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
            <Button
              type="submit"
              variant="outline"
              data-testid="search-btn"
            >
              <Search className="h-4 w-4" />
            </Button>
          </div>
        </form>

        {/* Filters Toggle */}
        <Button
          variant="outline"
          onClick={() => setShowFilters(!showFilters)}
          data-testid="filters-toggle"
        >
          <Filter className="h-4 w-4 mr-2" />
          Filters
        </Button>

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

      {/* Filters Panel */}
      {showFilters && (
        <Card className="p-4" data-testid="filters-panel">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium">Status</label>
              <Select value={statusFilter} onValueChange={handleStatusFilterChange}>
                <SelectTrigger>
                  <SelectValue placeholder="All Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="new">New</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </Card>
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

              {/* Interview History */}
              <div data-testid="interview-history-section">
                <h4 className="text-lg font-semibold mb-4">Interview History</h4>
                <div className="border rounded-lg" data-testid="interview-history-table">
                  <div className="p-4 text-center text-muted-foreground">
                    No interviews found for this candidate.
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex gap-2">
                <Button onClick={() => openEditModal(viewingCandidate)} data-testid="edit-candidate-button">
                  <Edit className="h-4 w-4 mr-2" />
                  Edit Candidate
                </Button>

                <Button variant="outline" data-testid="view-reports-button">
                  <Eye className="h-4 w-4 mr-2" />
                  View Reports
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


    </div>
  );
};
