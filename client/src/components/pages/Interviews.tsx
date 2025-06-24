import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
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
import { useDataLoaders } from '@/hooks/useDataLoaders';
import {
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  Copy,
  X,
  RefreshCw,
  Play,
  Pause,
  CheckCircle,
  XCircle
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import api, { InterviewResponse, InterviewListResponse } from '@/lib/api';
import { CreateInterviewModal } from '@/components/interviews/CreateInterviewModal';
import { InterviewDetailsModal } from '@/components/interviews/InterviewDetailsModal';
import { StatusChangeModal } from '@/components/interviews/StatusChangeModal';

export const Interviews: React.FC = () => {
  const [interviews, setInterviews] = useState<InterviewResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentTab, setCurrentTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedInterviews, setSelectedInterviews] = useState<number[]>([]);
  const [statusCounts, setStatusCounts] = useState<{ [key: string]: number }>({});
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedInterview, setSelectedInterview] = useState<InterviewResponse | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 10,
    total: 0,
    total_pages: 0
  });

  const { toast } = useToast();
  const {
    candidates,
    jobs,
    loadingCandidates,
    loadingJobs,
    loadCandidates,
    loadJobs,
    loadAllData
  } = useDataLoaders();



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
    const loadData = async () => {
      await Promise.all([
        loadAllData(),
        loadInterviews()
      ]);
    };

    loadData();
  }, [currentTab, searchTerm, pagination.page, loadAllData]);

  const handleTabChange = (value: string) => {
    setCurrentTab(value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleSearch = (value: string) => {
    setSearchTerm(value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { label: 'Pending', variant: 'secondary' as const },
      in_progress: { label: 'In Progress', variant: 'default' as const },
      completed: { label: 'Completed', variant: 'success' as const },
      cancelled: { label: 'Cancelled', variant: 'destructive' as const },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || { label: status, variant: 'secondary' as const };
    return <Badge variant={config.variant}>{config.label}</Badge>;
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

  const handleChangeStatus = (interview: InterviewResponse) => {
    setSelectedInterview(interview);
    setShowStatusModal(true);
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
                        <TableHead data-testid="candidate-header">Candidate</TableHead>
                        <TableHead data-testid="job-header">Job</TableHead>
                        <TableHead data-testid="status-header">Status</TableHead>
                        <TableHead data-testid="date-header">Date</TableHead>
                        <TableHead data-testid="pass-key-header">Pass Key</TableHead>
                        <TableHead data-testid="score-header">Score</TableHead>
                        <TableHead data-testid="risk-level-header">Risk Level</TableHead>
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
                          <TableCell data-testid="interview-candidate">
                            {interview.candidate_name ||
                             interview.candidate?.full_name ||
                             (interview.candidate?.first_name && interview.candidate?.last_name
                               ? `${interview.candidate.first_name} ${interview.candidate.last_name}`
                               : interview.candidate?.first_name || interview.candidate?.last_name || 'Unknown')}
                          </TableCell>
                          <TableCell data-testid="interview-job">
                            {interview.job_title || interview.job?.title || 'Unknown'}
                          </TableCell>
                          <TableCell data-testid="interview-status">
                            {getStatusBadge(interview.status)}
                          </TableCell>
                          <TableCell data-testid="interview-date">
                            {interview.interview_date ? new Date(interview.interview_date).toLocaleDateString() : 'Not scheduled'}
                          </TableCell>
                          <TableCell data-testid="interview-pass-key">
                            <div className="flex items-center gap-2">
                              <code className="bg-muted px-2 py-1 rounded text-sm">{interview.pass_key}</code>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  navigator.clipboard.writeText(interview.pass_key);
                                  toast({ title: 'Pass key copied to clipboard' });
                                }}
                                data-testid="copy-pass-key-btn"
                              >
                                <Copy className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                          <TableCell data-testid="interview-score">
                            {interview.score ? `${interview.score}%` : '-'}
                          </TableCell>
                          <TableCell data-testid="interview-risk-level">
                            {interview.risk_level ? (
                              <Badge variant={interview.risk_level === 'high' ? 'destructive' : interview.risk_level === 'medium' ? 'secondary' : 'success'}>
                                {interview.risk_level}
                              </Badge>
                            ) : '-'}
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
                                  onClick={() => handleChangeStatus(interview)}
                                  data-testid="change-status-btn"
                                >
                                  <Edit className="h-4 w-4 mr-2" />
                                  Change Status
                                </DropdownMenuItem>
                                {interview.status === 'pending' && (
                                  <DropdownMenuItem data-testid="cancel-interview-btn">
                                    <X className="h-4 w-4 mr-2" />
                                    Cancel
                                  </DropdownMenuItem>
                                )}
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
        candidates={candidates}
        jobs={jobs}
        loading={loadingCandidates || loadingJobs}
      />

      <InterviewDetailsModal
        open={showDetailsModal}
        onOpenChange={setShowDetailsModal}
        interview={selectedInterview}
      />

      <StatusChangeModal
        open={showStatusModal}
        onOpenChange={setShowStatusModal}
        interview={selectedInterview}
        onStatusChanged={loadInterviews}
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
            <div className="py-4">
              <p className="text-sm text-muted-foreground">
                <strong>Candidate:</strong> {selectedInterview.candidate_name || 'Unknown'}
              </p>
              <p className="text-sm text-muted-foreground">
                <strong>Job:</strong> {selectedInterview.job_title || 'Unknown'}
              </p>
              <p className="text-sm text-muted-foreground">
                <strong>Status:</strong> {selectedInterview.status}
              </p>
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
