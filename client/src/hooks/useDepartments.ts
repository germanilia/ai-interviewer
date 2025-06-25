import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

export interface UseDepartmentsReturn {
  departments: string[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const useDepartments = (): UseDepartmentsReturn => {
  const [departments, setDepartments] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { toast } = useToast();

  const fetchDepartments = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Since jobs are now part of interviews, we'll get departments from interviews
      const response = await api.interviews.getAll({ page_size: 1000 });
      const uniqueDepartments = [...new Set(
        response.items
          .map(interview => interview.job_department)
          .filter(dept => dept && dept.trim() !== '')
      )].sort();
      setDepartments(uniqueDepartments);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch departments';
      setError(errorMessage);
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchDepartments();
  }, [fetchDepartments]);

  return {
    departments,
    loading,
    error,
    refetch: fetchDepartments,
  };
};
