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