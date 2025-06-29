import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
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

import {
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  X,
  RefreshCw} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import api, { InterviewResponse, InterviewListResponse } from '@/lib/api';
import { InterviewDetailsModal } from '@/components/interviews/InterviewDetailsModal';
import { CreateInterviewModal } from '../interviews/CreateInterviewModal';
import { EditInterviewModal } from '../interviews/EditInterviewModal';

export const Interviews: React.FC = () => {
  const [interviews, setInterviews] = useState<InterviewResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentTab, setCurrentTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedInterviews, setSelectedInterviews] = useState<number[]>([]);
  const [statusCounts, setStatusCounts] = useState<{ [key: string]: number }>({});
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedInterview, setSelectedInterview] = useState<InterviewResponse | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 10,
    total: 0,
    total_pages: 0
  });

  const { toast } = useToast();
  // Remove unused data loaders since interviews now contain job info



  const loadInterviews = async () => {
    try {
      setLoading(true);
      const params: any = {
        page: pagination.page,
        page_size: pagination.page_size,
      };

      if (currentTab !== 'all') {
        params.status = currentTab === 'in-progress' ? 'in_progress' : currentTab;
      }

      if (searchTerm) {
        params.search = searchTerm;
      }

      const response: InterviewListResponse = await api.interviews.getAll(params);
      setInterviews(response.items || []);
      setPagination({
        page: response.page,
        page_size: response.page_size,
        total: response.total,
        total_pages: response.total_pages
      });
      setStatusCounts(response.status_counts || {});
    } catch (error) {
      console.error('Failed to load interviews:', error);
      toast({
        title: 'Error',
        description: 'Failed to load interviews',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInterviews();
  }, [currentTab, searchTerm, pagination.page]);

  const handleTabChange = (value: string) => {
    setCurrentTab(value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleSearch = (value: string) => {
    setSearchTerm(value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const getTabCount = (status: string) => {
    if (status === 'all') {
      return Object.values(statusCounts).reduce((sum, count) => sum + count, 0);
    }
    const key = status === 'in-progress' ? 'in_progress' : status;
    return statusCounts[key] || 0;
  };

  const handleViewDetails = (interview: InterviewResponse) => {
    setSelectedInterview(interview);
    setShowDetailsModal(true);
  };

  const handleEditInterview = (interview: InterviewResponse) => {
    setSelectedInterview(interview);
    setShowEditModal(true);
  };



  const handleDeleteInterview = (interview: InterviewResponse) => {
    setSelectedInterview(interview);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!selectedInterview) return;

    try {
      await api.interviews.delete(selectedInterview.id);
      toast({
        title: 'Success',
        description: 'Interview deleted successfully',
      });
      loadInterviews();
      setShowDeleteModal(false);
      setSelectedInterview(null);
    } catch (error) {
      console.error('Failed to delete interview:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete interview',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="space-y-6" data-testid="interviews-section">
      {loading && (
        <div data-testid="interviews-loading" className="flex items-center justify-center py-8">
          <div className="text-center space-y-2">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="text-sm text-muted-foreground">Loading interviews...</p>
          </div>
        </div>
      )}

      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground" data-testid="page-title">
            Interviews
          </h1>
          <p className="text-muted-foreground" data-testid="page-subtitle">
            Manage and monitor interview sessions
          </p>
        </div>
        <div className="flex items-center gap-2" data-testid="interviews-toolbar">
          <Button
            variant="outline"
            size="sm"
            onClick={loadInterviews}
            data-testid="refresh-interviews-btn"
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button
            className="flex items-center gap-2"
            onClick={() => setShowCreateModal(true)}
            data-testid="create-interview-btn"
          >
            <Plus className="h-4 w-4" />
            Create Interview
          </Button>
        </div>
      </div>

      {/* Search and Filter Bar */}
      <div className="flex items-center gap-4" data-testid="search-section">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search interviews..."
            className="pl-10"
            value={searchTerm}
            onChange={(e) => handleSearch(e.target.value)}
            data-testid="interviews-search"
          />
          {searchTerm && (
            <Button
              variant="ghost"
              size="sm"
              className="absolute right-2 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
              onClick={() => handleSearch('')}
              data-testid="clear-search-btn"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
        <Button variant="outline" className="flex items-center gap-2" data-testid="filters-toggle">
          <Filter className="h-4 w-4" />
          Filter
        </Button>
        <Button variant="outline" size="sm" data-testid="search-btn">
          <Search className="h-4 w-4" />
        </Button>
      </div>

      {/* Bulk Actions Bar */}
      {selectedInterviews.length > 0 && (
        <div className="flex items-center justify-between p-4 bg-muted rounded-lg" data-testid="bulk-actions-bar">
          <span data-testid="selected-count">{selectedInterviews.length} interviews selected</span>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" data-testid="bulk-cancel-btn">
              Cancel Selected
            </Button>
            <Button variant="outline" size="sm" data-testid="bulk-delete-btn">
              Delete Selected
            </Button>
            <Button variant="outline" size="sm" data-testid="bulk-export-btn">
              Export Selected
            </Button>
          </div>
        </div>
      )}

      {/* Interview Status Tabs */}
      <Tabs value={currentTab} onValueChange={handleTabChange} className="w-full">
        <TabsList className="grid w-full grid-cols-5" data-testid="status-tabs">
          <TabsTrigger value="all" data-testid="all-interviews-tab">
            All ({getTabCount('all')})
          </TabsTrigger>
          <TabsTrigger value="pending" data-testid="pending-tab">
            Pending ({getTabCount('pending')})
          </TabsTrigger>
          <TabsTrigger value="in-progress" data-testid="in-progress-tab">
            In Progress ({getTabCount('in-progress')})
          </TabsTrigger>
          <TabsTrigger value="completed" data-testid="completed-tab">
            Completed ({getTabCount('completed')})
          </TabsTrigger>
          <TabsTrigger value="cancelled" data-testid="cancelled-tab">
            Cancelled ({getTabCount('cancelled')})
          </TabsTrigger>
        </TabsList>

        {/* Single table content for all tabs to prevent layout shifts */}
        <TabsContent value={currentTab} className="space-y-4">
          <Card data-testid="interviews-list">
            <CardContent className="p-0">
              <div className="min-h-[400px]">
                {interviews.length === 0 ? (
                  <div className="flex items-center justify-center h-[400px]" data-testid="interviews-empty-state">
                    <div className="text-center">
                      <p className="text-muted-foreground mb-4">
                        No interviews found. Create your first interview to get started.
                      </p>
                      <Button
                        onClick={() => setShowCreateModal(true)}
                        data-testid="empty-state-create-btn"
                      >
                        Create First Interview
                      </Button>
                    </div>
                  </div>
                ) : (
                  <Table data-testid="interviews-table">
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-12">
                          <Checkbox
                            checked={selectedInterviews.length === interviews.length && interviews.length > 0}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setSelectedInterviews(interviews.map(i => i.id));
                              } else {
                                setSelectedInterviews([]);
                              }
                            }}
                            data-testid="select-all-checkbox"
                          />
                        </TableHead>
                        <TableHead data-testid="job-title-header">Job Title</TableHead>
                        <TableHead data-testid="department-header">Department</TableHead>
                        <TableHead data-testid="candidates-header">Candidates</TableHead>
                        <TableHead data-testid="questions-header">Questions</TableHead>
                        <TableHead data-testid="avg-score-header">Avg Score</TableHead>
                        <TableHead data-testid="completion-header">Completion</TableHead>
                        <TableHead data-testid="created-header">Created</TableHead>
                        <TableHead data-testid="actions-header">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {interviews.map((interview) => (
                        <TableRow key={interview.id} data-testid="interview-row">
                          <TableCell>
                            <Checkbox
                              checked={selectedInterviews.includes(interview.id)}
                              onCheckedChange={(checked) => {
                                if (checked) {
                                  setSelectedInterviews(prev => [...prev, interview.id]);
                                } else {
                                  setSelectedInterviews(prev => prev.filter(id => id !== interview.id));
                                }
                              }}
                              data-testid="interview-checkbox"
                            />
                          </TableCell>
                          <TableCell data-testid="interview-job-title">
                            <div>
                              <div className="font-medium">{interview.job_title}</div>
                              {interview.job_description && (
                                <div className="text-sm text-muted-foreground line-clamp-1">
                                  {interview.job_description}
                                </div>
                              )}
                            </div>
                          </TableCell>
                          <TableCell data-testid="interview-department">
                            {interview.job_department ? (
                              <Badge variant="secondary">{interview.job_department}</Badge>
                            ) : (
                              <span className="text-muted-foreground">-</span>
                            )}
                          </TableCell>
                          <TableCell data-testid="interview-candidates">
                            <div className="flex items-center gap-2">
                              <span>{interview.completed_candidates}/{interview.total_candidates}</span>
                              <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-primary transition-all"
                                  style={{
                                    width: interview.total_candidates > 0
                                      ? `${(interview.completed_candidates / interview.total_candidates) * 100}%`
                                      : '0%'
                                  }}
                                />
                              </div>
                            </div>
                          </TableCell>
                          <TableCell data-testid="interview-questions">
                            <Badge variant="outline">{interview.questions_count || 0} questions</Badge>
                          </TableCell>
                          <TableCell data-testid="interview-avg-score">
                            {interview.avg_score ? `${interview.avg_score}%` : '-'}
                          </TableCell>
                          <TableCell data-testid="interview-completion">
                            <div className="text-sm">
                              {interview.total_candidates > 0 ? (
                                <span className={interview.completed_candidates === interview.total_candidates ? 'text-green-600' : 'text-muted-foreground'}>
                                  {Math.round((interview.completed_candidates / interview.total_candidates) * 100)}%
                                </span>
                              ) : (
                                <span className="text-muted-foreground">No candidates</span>
                              )}
                            </div>
                          </TableCell>
                          <TableCell data-testid="interview-created">
                            {new Date(interview.created_at).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="sm">
                                  <MoreHorizontal className="h-4 w-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuItem
                                  onClick={() => handleViewDetails(interview)}
                                  data-testid="view-details-btn"
                                >
                                  <Eye className="h-4 w-4 mr-2" />
                                  View Details
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                  onClick={() => handleEditInterview(interview)}
                                  data-testid="edit-interview-btn"
                                >
                                  <Edit className="h-4 w-4 mr-2" />
                                  Edit Interview
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                  className="text-destructive"
                                  onClick={() => handleDeleteInterview(interview)}
                                  data-testid="delete-interview-btn"
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
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Interviews</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{pagination.total}</div>
            <p className="text-xs text-muted-foreground">All time</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{statusCounts.in_progress || 0}</div>
            <p className="text-xs text-muted-foreground">Active now</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{statusCounts.completed || 0}</div>
            <p className="text-xs text-muted-foreground">Total completed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{statusCounts.pending || 0}</div>
            <p className="text-xs text-muted-foreground">Waiting to start</p>
          </CardContent>
        </Card>
      </div>

      {/* Modals */}
      <CreateInterviewModal
        open={showCreateModal}
        onOpenChange={setShowCreateModal}
        onInterviewCreated={loadInterviews}
      />

      <EditInterviewModal
        open={showEditModal}
        onOpenChange={setShowEditModal}
        interview={selectedInterview}
        onInterviewUpdated={loadInterviews}
      />

      <InterviewDetailsModal
        open={showDetailsModal}
        onOpenChange={setShowDetailsModal}
        interview={selectedInterview}
      />

      {/* Delete Confirmation Modal */}
      <Dialog open={showDeleteModal} onOpenChange={setShowDeleteModal}>
        <DialogContent className="sm:max-w-[400px]" data-testid="delete-interview-modal">
          <DialogHeader>
            <DialogTitle>Delete Interview</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this interview? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          {selectedInterview && (
            <div className="py-4 space-y-3">
              <div>
                <p className="text-sm font-medium">Job Title</p>
                <p className="text-sm text-muted-foreground">{selectedInterview.job_title}</p>
              </div>
              {selectedInterview.job_department && (
                <div>
                  <p className="text-sm font-medium">Department</p>
                  <p className="text-sm text-muted-foreground">{selectedInterview.job_department}</p>
                </div>
              )}
              {selectedInterview.job_description && (
                <div>
                  <p className="text-sm font-medium">Job Description</p>
                  <p className="text-sm text-muted-foreground">{selectedInterview.job_description}</p>
                </div>
              )}
              <div>
                <p className="text-sm font-medium">Candidates</p>
                <p className="text-sm text-muted-foreground">
                  {selectedInterview.completed_candidates} completed / {selectedInterview.total_candidates} total
                </p>
              </div>
              {selectedInterview.avg_score && (
                <div>
                  <p className="text-sm font-medium">Average Score</p>
                  <p className="text-sm text-muted-foreground">{selectedInterview.avg_score}%</p>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowDeleteModal(false)}
              data-testid="cancel-delete-btn"
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={confirmDelete}
              data-testid="confirm-delete-btn"
            >
              Delete Interview
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
