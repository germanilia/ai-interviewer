import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { UserCheck, Key } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';

interface CandidateLoginResponse {
  candidate_id: number;
  candidate_name: string;
  interview_id: number;
  interview_title: string;
  session_id?: number;
  message: string;
}

export const InterviewLanding: React.FC = () => {
  const [passKey, setPassKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleCandidateLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!passKey.trim()) {
      toast({
        title: "Error",
        description: "Please enter your pass key",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const response: CandidateLoginResponse = await api.interviewSession.candidateLogin({
        pass_key: passKey.trim()
      });

      toast({
        title: "Login Successful",
        description: response.message,
      });

      // Navigate to candidate chat interface with context
      navigate('/interview/chat', {
        state: {
          candidateId: response.candidate_id,
          candidateName: response.candidate_name,
          interviewId: response.interview_id,
          interviewTitle: response.interview_title,
          sessionId: response.session_id
        }
      });
    } catch (error) {
      console.error('Candidate login error:', error);
      toast({
        title: "Login Failed",
        description: error instanceof Error ? error.message : "Invalid pass key. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleOperatorLogin = () => {
    // Navigate to the regular login page
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-5xl">
        <div className="grid md:grid-cols-2 gap-8 items-stretch">
          {/* Candidate Login */}
          <Card className="w-full shadow-xl border-0 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm h-full" data-testid="candidate-login-card">
          <CardHeader className="text-center space-y-6 pb-6">
            <div className="mx-auto w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center shadow-lg">
              <Key className="w-10 h-10 text-white" />
            </div>
            <div>
              <CardTitle className="text-2xl font-bold text-slate-800 dark:text-slate-100">
                Candidate Access
              </CardTitle>
              <CardDescription className="text-slate-600 dark:text-slate-300 text-base">
                Enter your unique pass key to start your interview
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <form onSubmit={handleCandidateLogin} className="space-y-6">
              <div className="space-y-3">
                <Label htmlFor="passKey" className="text-sm font-semibold text-slate-700 dark:text-slate-200">Pass Key</Label>
                <Input
                  id="passKey"
                  type="text"
                  placeholder="Enter your pass key"
                  value={passKey}
                  onChange={(e) => setPassKey(e.target.value)}
                  disabled={isLoading}
                  data-testid="pass-key-input"
                  className="w-full h-12 text-base border-2 border-slate-200 dark:border-slate-600 focus:border-blue-500 dark:focus:border-blue-400 bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 text-center font-mono tracking-wider"
                />
              </div>
              <Button
                type="submit"
                className="w-full h-12 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold text-base shadow-lg transition-all duration-200"
                disabled={isLoading}
                data-testid="candidate-login-button"
              >
                {isLoading ? "Logging in..." : "Start Interview"}
              </Button>
            </form>
          </CardContent>
          </Card>

          {/* Operator Login */}
          <Card className="w-full shadow-xl border-0 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm h-full" data-testid="operator-login-card">
          <CardHeader className="text-center space-y-6 pb-6">
            <div className="mx-auto w-20 h-20 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-full flex items-center justify-center shadow-lg">
              <UserCheck className="w-10 h-10 text-white" />
            </div>
            <div>
              <CardTitle className="text-2xl font-bold text-slate-800 dark:text-slate-100">
                Operator Access
              </CardTitle>
              <CardDescription className="text-slate-600 dark:text-slate-300 text-base">
                Access the admin dashboard to manage interviews
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-3">
              <div className="text-center text-sm text-slate-600 dark:text-slate-300 font-medium">
                Sign in with your operator credentials to access:
              </div>
              <ul className="text-sm text-slate-500 dark:text-slate-400 space-y-2 ml-4">
                <li>• Interview management</li>
                <li>• Candidate monitoring</li>
                <li>• Reports and analytics</li>
                <li>• Question management</li>
              </ul>
            </div>
            <Button
              onClick={handleOperatorLogin}
              className="w-full h-12 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 text-white font-semibold text-base shadow-lg transition-all duration-200"
              data-testid="operator-login-button"
            >
              Operator Sign In
            </Button>
          </CardContent>
          </Card>
        </div>

        {/* Separator */}
        <div className="flex items-center justify-center my-12">
          <div className="flex items-center space-x-6">
            <Separator className="flex-1 max-w-24 bg-slate-300 dark:bg-slate-600" />
            <span className="text-sm text-slate-500 dark:text-slate-400 font-medium bg-white/90 dark:bg-slate-800/90 px-4 py-2 rounded-full border border-slate-200 dark:border-slate-600 shadow-sm">
              OR
            </span>
            <Separator className="flex-1 max-w-24 bg-slate-300 dark:bg-slate-600" />
          </div>
        </div>
      </div>
    </div>
  );
};
