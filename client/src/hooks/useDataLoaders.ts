import { useState, useCallback } from 'react';
import { useToast } from '@/hooks/use-toast';
import api from '@/lib/api';

export interface UseDataLoadersReturn {
  candidates: any[];
  jobs: any[];
  loadingCandidates: boolean;
  loadingJobs: boolean;
  loadCandidates: () => Promise<void>;
  loadJobs: () => Promise<void>;
  loadAllData: () => Promise<void>;
}

export const useDataLoaders = (): UseDataLoadersReturn => {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [loadingCandidates, setLoadingCandidates] = useState(false);
  const [loadingJobs, setLoadingJobs] = useState(false);

  const { toast } = useToast();

  const loadCandidates = useCallback(async () => {
    try {
      setLoadingCandidates(true);
      const response = await api.candidates.getAll({ page_size: 100 });
      setCandidates(response.items || []);
    } catch (error) {
      console.error('Failed to load candidates:', error);
      toast({
        title: 'Error',
        description: 'Failed to load candidates',
        variant: 'destructive',
      });
    } finally {
      setLoadingCandidates(false);
    }
  }, [toast]);

  const loadJobs = useCallback(async () => {
    try {
      setLoadingJobs(true);
      const response = await api.jobs.getAll({ page_size: 100 });
      setJobs(response.jobs || []);
    } catch (error) {
      console.error('Failed to load jobs:', error);
      toast({
        title: 'Error',
        description: 'Failed to load jobs',
        variant: 'destructive',
      });
    } finally {
      setLoadingJobs(false);
    }
  }, [toast]);

  const loadAllData = useCallback(async () => {
    await Promise.all([loadCandidates(), loadJobs()]);
  }, [loadCandidates, loadJobs]);

  return {
    candidates,
    jobs,
    loadingCandidates,
    loadingJobs,
    loadCandidates,
    loadJobs,
    loadAllData,
  };
};
