import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';

import { Send, User, Bot, LogOut, Sun, Moon, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';
import { useTheme } from '@/contexts/ThemeContext';

// Utility function to detect text direction and language
const detectTextDirection = (text: string): { direction: 'ltr' | 'rtl'; language: 'en' | 'he' | 'ar' | 'other' } => {
  // Hebrew Unicode range: \u0590-\u05FF
  // Arabic Unicode range: \u0600-\u06FF, \u0750-\u077F, \u08A0-\u08FF
  const hebrewRegex = /[\u0590-\u05FF]/;
  const arabicRegex = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/;

  const hasHebrew = hebrewRegex.test(text);
  const hasArabic = arabicRegex.test(text);

  if (hasHebrew) {
    return { direction: 'rtl', language: 'he' };
  } else if (hasArabic) {
    return { direction: 'rtl', language: 'ar' };
  } else {
    return { direction: 'ltr', language: 'en' };
  }
};

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  question_id?: number;
  direction?: 'ltr' | 'rtl';
  language?: 'en' | 'he' | 'ar' | 'other';
}

interface InterviewState {
  candidateId: number;
  candidateName: string;
  interviewId: number;
  interviewTitle: string;
  sessionId?: number;
}

interface ChatResponse {
  session_id: number;
  assistant_message: string;
  session_status: string;
  is_interview_complete: boolean;
}

export const CandidateChat: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { setTheme, actualTheme } = useTheme();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [interviewState, setInterviewState] = useState<InterviewState | null>(null);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isEndingInterview, setIsEndingInterview] = useState(false);
  const [isInterviewComplete, setIsInterviewComplete] = useState(false);

  useEffect(() => {
    // Get interview state from navigation
    const state = location.state as InterviewState;
    if (!state) {
      toast({
        title: "Error",
        description: "No interview session found. Please log in again.",
        variant: "destructive",
      });
      navigate('/interview');
      return;
    }

    setInterviewState(state);
    initializeSession(state);
  }, [location.state, navigate, toast]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeSession = async (state: InterviewState) => {
    try {
      if (!state.sessionId) {
        // This should not happen anymore since login creates a session
        toast({
          title: "Error",
          description: "No session found. Please log in again.",
          variant: "destructive",
        });
        navigate('/interview');
        return;
      }

      // Set the session ID from login
      setSessionId(state.sessionId);

      // Load conversation history from session
      try {
        const sessionData = await api.interviewSession.getSession(state.sessionId);
        if (sessionData.conversation_history && sessionData.conversation_history.length > 0) {
          const chatMessages: ChatMessage[] = sessionData.conversation_history.map((msg: any) => {
            // Detect text direction and language for each loaded message
            const textInfo = detectTextDirection(msg.content);
            return {
              role: msg.role,
              content: msg.content,
              timestamp: msg.timestamp,
              direction: textInfo.direction,
              language: textInfo.language
            };
          });
          setMessages(chatMessages);
        } else {
          // No conversation history yet - this shouldn't happen since we add initial message on session creation
          setMessages([]);
        }
      } catch (error) {
        console.error('Failed to load conversation history:', error);
        // Fallback to empty messages if loading fails
        setMessages([]);
      }

    } catch (error) {
      console.error('Failed to initialize session:', error);
      toast({
        title: "Error",
        description: "Failed to start interview session. Please try again.",
        variant: "destructive",
      });
      navigate('/interview');
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentMessage.trim() || !sessionId || isLoading || isInterviewComplete) {
      return;
    }

    // Detect text direction and language
    const textInfo = detectTextDirection(currentMessage.trim());

    const userMessage: ChatMessage = {
      role: 'user',
      content: currentMessage.trim(),
      timestamp: new Date().toISOString(),
      direction: textInfo.direction,
      language: textInfo.language
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const response: ChatResponse = await api.interviewSession.chat({
        session_id: sessionId,
        message: userMessage.content,
        language: textInfo.language // Send language preference to backend
      });

      // Detect direction for assistant response as well
      const assistantTextInfo = detectTextDirection(response.assistant_message);

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.assistant_message,
        timestamp: new Date().toISOString(),
        direction: assistantTextInfo.direction,
        language: assistantTextInfo.language
      };

      setMessages(prev => [...prev, assistantMessage]);

      if (response.is_interview_complete) {
        setIsInterviewComplete(true);
        toast({
          title: "Interview Complete",
          description: "Thank you for completing the interview. You may now close this window.",
        });
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleEndInterview = async () => {
    if (!interviewState?.sessionId) {
      navigate('/interview');
      return;
    }

    setIsEndingInterview(true);
    try {
      await api.interviewSession.endSession({
        session_id: interviewState.sessionId
      });

      toast({
        title: "Interview Ended",
        description: "Your interview has been completed successfully.",
      });

      navigate('/interview');
    } catch (error) {
      console.error('Failed to end interview:', error);
      toast({
        title: "Error",
        description: "Failed to end interview. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsEndingInterview(false);
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  if (!interviewState) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 flex flex-col">
      {/* Header */}
      <Card className="rounded-none border-0 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm shadow-lg">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl font-semibold text-slate-800 dark:text-slate-100">
                {interviewState.interviewTitle}
              </CardTitle>
              <p className="text-sm text-slate-600 dark:text-slate-300">
                Candidate: {interviewState.candidateName}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setTheme(actualTheme === "light" ? "dark" : "light")}
                data-testid="theme-toggle-button"
                className="text-slate-600 dark:text-slate-300 hover:text-slate-800 dark:hover:text-slate-100"
              >
                {actualTheme === "light" ? (
                  <Moon className="w-4 h-4" />
                ) : (
                  <Sun className="w-4 h-4" />
                )}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleEndInterview}
                disabled={isEndingInterview}
                data-testid="end-interview-button"
                className="border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700"
              >
                {isEndingInterview ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Ending Interview...
                  </>
                ) : (
                  <>
                    <LogOut className="w-4 h-4 mr-2" />
                    End Interview
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Chat Messages */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full p-6">
        <ScrollArea className="flex-1 pr-4" data-testid="chat-messages">
          <div className="space-y-6">
            {messages.map((message, index) => {
              const isRTL = message.direction === 'rtl';
              const isUser = message.role === 'user';

              // For RTL languages: incoming (assistant) on left, outgoing (user) on right
              // For LTR languages: incoming (assistant) on right, outgoing (user) on left
              const shouldAlignRight = isRTL ? isUser : !isUser;

              return (
                <div
                  key={index}
                  className={`flex mb-4 ${shouldAlignRight ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`flex max-w-[85%] ${shouldAlignRight ? 'flex-row-reverse' : 'flex-row'}`}
                  >
                    <div
                      className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-md ${
                        isUser
                          ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                          : 'bg-gradient-to-br from-emerald-500 to-emerald-600 text-white'
                      } ${shouldAlignRight ? 'ml-3' : 'mr-3'}`}
                    >
                      {isUser ? (
                        <User className="w-5 h-5" />
                      ) : (
                        <Bot className="w-5 h-5" />
                      )}
                    </div>
                    <div
                      className={`rounded-2xl px-4 py-3 shadow-sm ${
                        isUser
                          ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                          : 'bg-white/80 dark:bg-slate-700/80 backdrop-blur-sm border border-slate-200 dark:border-slate-600 text-slate-800 dark:text-slate-100'
                      }`}
                      dir={isRTL ? 'rtl' : 'ltr'}
                    >
                      <p
                        className={`text-sm leading-relaxed ${isRTL ? 'text-right' : 'text-left'}`}
                        dir={isRTL ? 'rtl' : 'ltr'}
                      >
                        {message.content}
                      </p>
                      <p
                        className={`text-xs mt-2 ${
                          isUser
                            ? 'text-blue-100'
                            : 'text-slate-500 dark:text-slate-400'
                        } ${isRTL ? 'text-left' : 'text-right'}`}
                        dir="ltr"
                      >
                        {formatTime(message.timestamp)}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex flex-row">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-gradient-to-br from-emerald-500 to-emerald-600 text-white mr-3 shadow-md">
                    <Bot className="w-5 h-5" />
                  </div>
                  <div className="bg-white/80 dark:bg-slate-700/80 backdrop-blur-sm border border-slate-200 dark:border-slate-600 shadow-sm rounded-2xl px-4 py-3">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-emerald-500 dark:bg-emerald-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-emerald-500 dark:bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-emerald-500 dark:bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Message Input */}
        <Card className="mt-6 shadow-xl border-0 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm">
          <CardContent className="p-6">
            <form onSubmit={sendMessage} className="flex space-x-3">
              <Input
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                placeholder={
                  isInterviewComplete
                    ? "Interview completed"
                    : "Type your response..."
                }
                disabled={isLoading || isInterviewComplete}
                data-testid="message-input"
                className="flex-1 h-12 text-base border-2 border-slate-200 dark:border-slate-600 focus:border-blue-500 dark:focus:border-blue-400 bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 rounded-xl"
                dir={currentMessage ? detectTextDirection(currentMessage).direction : 'ltr'}
                style={{
                  textAlign: currentMessage ? (detectTextDirection(currentMessage).direction === 'rtl' ? 'right' : 'left') : 'left'
                }}
              />
              <Button
                type="submit"
                disabled={isLoading || !currentMessage.trim() || isInterviewComplete}
                data-testid="send-message-button"
                className="h-12 px-6 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold shadow-lg transition-all duration-200 rounded-xl"
              >
                <Send className="w-5 h-5" />
              </Button>
            </form>
            {isInterviewComplete && (
              <p className="text-sm text-emerald-600 dark:text-emerald-400 mt-4 text-center font-medium">
                Interview completed successfully. Thank you for your time!
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
