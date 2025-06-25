import { useState, useCallback } from 'react';
import { useToast } from '@/hooks/use-toast';
import api from '@/lib/api';

export interface UseDataLoadersReturn {
  candidates: any[];
  interviews: any[];
  loadingCandidates: boolean;
  loadingInterviews: boolean;
  loadCandidates: () => Promise<void>;
  loadInterviews: () => Promise<void>;
  loadAllData: () => Promise<void>;
}

export const useDataLoaders = (): UseDataLoadersReturn => {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [interviews, setInterviews] = useState<any[]>([]);
  const [loadingCandidates, setLoadingCandidates] = useState(false);
  const [loadingInterviews, setLoadingInterviews] = useState(false);

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

  const loadInterviews = useCallback(async () => {
    try {
      setLoadingInterviews(true);
      const response = await api.interviews.getAll({ page_size: 100 });
      setInterviews(response.items || []);
    } catch (error) {
      console.error('Failed to load interviews:', error);
      toast({
        title: 'Error',
        description: 'Failed to load interviews',
        variant: 'destructive',
      });
    } finally {
      setLoadingInterviews(false);
    }
  }, [toast]);

  const loadAllData = useCallback(async () => {
    await Promise.all([loadCandidates(), loadInterviews()]);
  }, [loadCandidates, loadInterviews]);

  return {
    candidates,
    interviews,
    loadingCandidates,
    loadingInterviews,
    loadCandidates,
    loadInterviews,
    loadAllData,
  };
};
