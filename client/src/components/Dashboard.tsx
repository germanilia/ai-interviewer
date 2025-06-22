import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';
import UserList from '@/components/UserList';
import StatusComponent from '@/components/StatusComponent';

export const Dashboard: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back, {user?.full_name || user?.email}
        </p>
      </div>

      {/* User Info Card */}
      <Card>
            <CardHeader>
              <CardTitle>User Information</CardTitle>
              <CardDescription>
                Your account details and role information
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Email</label>
                  <p className="text-sm text-foreground">{user?.email}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Full Name</label>
                  <p className="text-sm text-foreground">{user?.full_name || 'Not provided'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Role</label>
                  <p className="text-sm text-foreground capitalize">{user?.role}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Status</label>
                  <p className="text-sm text-foreground">
                    {user?.is_active ? (
                      <span className="text-green-600 dark:text-green-400">Active</span>
                    ) : (
                      <span className="text-red-600 dark:text-red-400">Inactive</span>
                    )}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* API Status */}
          <Card>
            <CardHeader>
              <CardTitle>System Status</CardTitle>
              <CardDescription>
                Backend API connection status
              </CardDescription>
            </CardHeader>
            <CardContent>
              <StatusComponent />
            </CardContent>
          </Card>

          {/* Users List (if admin) */}
          {user?.role === 'admin' && (
            <Card>
              <CardHeader>
                <CardTitle>Users Management</CardTitle>
                <CardDescription>
                  Manage system users (Admin only)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <UserList />
              </CardContent>
            </Card>
          )}

          {/* Regular user content */}
          {user?.role === 'user' && (
            <Card>
              <CardHeader>
                <CardTitle>Welcome!</CardTitle>
                <CardDescription>
                  You're successfully logged in as a user
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  This is your dashboard. More features will be added here.
                </p>
              </CardContent>
            </Card>
          )}
    </div>
  );
};
