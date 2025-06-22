import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/contexts/AuthContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { LoginForm } from '@/components/auth/LoginForm';
import { RegisterForm } from '@/components/auth/RegisterForm';
import { ConfirmSignUpForm } from '@/components/auth/ConfirmSignUpForm';
import { AppLayout } from '@/components/layout/AppLayout';
import { Dashboard } from '@/components/Dashboard';
import { Analytics } from '@/components/pages/Analytics';
import { Documents } from '@/components/pages/Documents';
import { DataLibrary } from '@/components/pages/DataLibrary';
import { Settings } from '@/components/pages/Settings';
import UserList from '@/components/UserList';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-background text-foreground">
          <Routes>
            {/* Public routes (redirect to dashboard if authenticated) */}
            <Route
              path="/login"
              element={
                <ProtectedRoute requireAuth={false}>
                  <LoginForm />
                </ProtectedRoute>
              }
            />
            <Route
              path="/register"
              element={
                <ProtectedRoute requireAuth={false}>
                  <RegisterForm />
                </ProtectedRoute>
              }
            />
            <Route
              path="/confirm-signup"
              element={
                <ProtectedRoute requireAuth={false}>
                  <ConfirmSignUpForm />
                </ProtectedRoute>
              }
            />

            {/* Protected routes with layout */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Dashboard />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Analytics />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/documents"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Documents />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/data-library"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <DataLibrary />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/users"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <UserList />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Settings />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/help"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <div className="space-y-6">
                      <div>
                        <h1 className="text-3xl font-bold text-foreground">Help & Support</h1>
                        <p className="text-muted-foreground">
                          Get help and find answers to common questions
                        </p>
                      </div>
                      <div className="text-center py-12">
                        <p className="text-muted-foreground">Help documentation coming soon...</p>
                      </div>
                    </div>
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            {/* Default redirects */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;