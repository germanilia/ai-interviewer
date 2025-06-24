import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import { 
  Monitor, 
  RefreshCw, 
  Clock, 
  User, 
  MessageSquare, 
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import api, { InterviewResponse } from '@/lib/api';

interface InterviewMonitoringModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  interview: InterviewResponse | null;
}

interface MonitoringData {
  status: string;
  progress: number;
  current_question?: string;
  questions_answered: number;
  total_questions: number;
  time_elapsed: number;
  estimated_time_remaining: number;
  candidate_responses?: any[];
  risk_indicators?: string[];
  technical_issues?: string[];
  last_activity: string;
}

export const InterviewMonitoringModal: React.FC<InterviewMonitoringModalProps> = ({
  open,
  onOpenChange,
  interview,
}) => {
  const [monitoringData, setMonitoringData] = useState<MonitoringData | null>(null);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const { toast } = useToast();

  useEffect(() => {
    if (open && interview) {
      loadMonitoringData();
      
      if (autoRefresh) {
        const interval = setInterval(loadMonitoringData, 5000); // Refresh every 5 seconds
        return () => clearInterval(interval);
      }
    }
  }, [open, interview, autoRefresh]);

  const loadMonitoringData = async () => {
    if (!interview) return;

    try {
      setLoading(true);
      const data = await api.interviews.monitor(interview.id);
      setMonitoringData(data);
    } catch (error) {
      console.error('Failed to load monitoring data:', error);
      toast({
        title: 'Error',
        description: 'Failed to load monitoring data',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    }
    return `${minutes}m ${secs}s`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'in_progress':
        return 'text-blue-600';
      case 'completed':
        return 'text-green-600';
      case 'cancelled':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  if (!interview) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[800px] max-h-[80vh] overflow-y-auto" data-testid="monitoring-modal">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2" data-testid="monitoring-title">
            <Monitor className="h-5 w-5" />
            Interview Monitoring
          </DialogTitle>
          <DialogDescription>
            Real-time monitoring for {interview.candidate?.full_name || 'Unknown Candidate'}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Status Overview */}
          <Card data-testid="status-overview">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Status Overview</CardTitle>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={loadMonitoringData}
                    disabled={loading}
                    data-testid="refresh-monitoring-btn"
                  >
                    <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                  </Button>
                  <Button
                    variant={autoRefresh ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setAutoRefresh(!autoRefresh)}
                    data-testid="auto-refresh-toggle"
                  >
                    Auto Refresh
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center" data-testid="interview-status">
                  <div className={`text-2xl font-bold ${getStatusColor(interview.status)}`}>
                    {interview.status.replace('_', ' ').toUpperCase()}
                  </div>
                  <p className="text-sm text-muted-foreground">Status</p>
                </div>
                
                <div className="text-center" data-testid="time-elapsed">
                  <div className="text-2xl font-bold">
                    {monitoringData ? formatTime(monitoringData.time_elapsed) : '--'}
                  </div>
                  <p className="text-sm text-muted-foreground">Time Elapsed</p>
                </div>
                
                <div className="text-center" data-testid="questions-progress">
                  <div className="text-2xl font-bold">
                    {monitoringData ? `${monitoringData.questions_answered}/${monitoringData.total_questions}` : '--'}
                  </div>
                  <p className="text-sm text-muted-foreground">Questions</p>
                </div>
                
                <div className="text-center" data-testid="completion-progress">
                  <div className="text-2xl font-bold">
                    {monitoringData ? `${monitoringData.progress}%` : '--'}
                  </div>
                  <p className="text-sm text-muted-foreground">Progress</p>
                </div>
              </div>

              {monitoringData && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Interview Progress</span>
                    <span>{monitoringData.progress}%</span>
                  </div>
                  <Progress value={monitoringData.progress} data-testid="progress-bar" />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Current Activity */}
          {monitoringData?.current_question && (
            <Card data-testid="current-activity">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  Current Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="font-medium">Current Question:</p>
                  <p className="text-sm bg-muted p-3 rounded" data-testid="current-question">
                    {monitoringData.current_question}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Last activity: {new Date(monitoringData.last_activity).toLocaleString()}
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Risk Indicators */}
          {monitoringData?.risk_indicators && monitoringData.risk_indicators.length > 0 && (
            <Card data-testid="risk-indicators">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-orange-600">
                  <AlertTriangle className="h-5 w-5" />
                  Risk Indicators
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {monitoringData.risk_indicators.map((indicator, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-orange-500" />
                      <span className="text-sm" data-testid="risk-indicator">
                        {indicator}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Technical Issues */}
          {monitoringData?.technical_issues && monitoringData.technical_issues.length > 0 && (
            <Card data-testid="technical-issues">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-red-600">
                  <XCircle className="h-5 w-5" />
                  Technical Issues
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {monitoringData.technical_issues.map((issue, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <XCircle className="h-4 w-4 text-red-500" />
                      <span className="text-sm" data-testid="technical-issue">
                        {issue}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Interview Details */}
          <Card data-testid="interview-details">
            <CardHeader>
              <CardTitle>Interview Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Candidate:</span>
                  <span className="ml-2" data-testid="candidate-name">
                    {interview.candidate?.full_name || 'Unknown'}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Job:</span>
                  <span className="ml-2" data-testid="job-title">
                    {interview.job?.title || 'Unknown'}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Pass Key:</span>
                  <code className="ml-2 bg-muted px-2 py-1 rounded text-xs" data-testid="pass-key">
                    {interview.pass_key}
                  </code>
                </div>
                <div>
                  <span className="font-medium">Created:</span>
                  <span className="ml-2" data-testid="created-date">
                    {new Date(interview.created_at).toLocaleString()}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="flex justify-end pt-4">
          <Button onClick={() => onOpenChange(false)} data-testid="close-monitoring-btn">
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
