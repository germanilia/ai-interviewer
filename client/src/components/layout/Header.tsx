import React from 'react';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { useSidebar } from '@/contexts/SidebarContext';
import { useAuth } from '@/contexts/AuthContext';

export const Header: React.FC = () => {
  const { toggle, isMobile } = useSidebar();
  const { user, signOut } = useAuth();

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error('Sign out error:', error);
    }
  };

  return (
    <header className="h-16 bg-card border-b border-border flex items-center justify-between px-4 lg:px-6">
      {/* Left side - Mobile menu button */}
      <div className="flex items-center gap-4">
        {isMobile && (
          <Button
            variant="ghost"
            size="icon"
            onClick={toggle}
            className="h-8 w-8"
            data-testid="mobile-menu-btn"
            aria-label="Toggle navigation menu"
          >
            <Menu className="h-4 w-4" />
            <span className="sr-only">Toggle navigation menu</span>
          </Button>
        )}
        
        {/* Breadcrumb or page title could go here */}
        <div className="hidden sm:block">
          <h1 className="text-lg font-semibold text-foreground">
            AI Interviewer
          </h1>
        </div>
      </div>

      {/* Right side - User info and actions */}
      <div className="flex items-center gap-4" data-testid="user-menu">
        <div className="hidden sm:flex items-center gap-2">
          <span className="text-sm text-muted-foreground">
            Welcome, {user?.full_name || user?.email}
          </span>
          <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
            {user?.role}
          </span>
        </div>

        <ThemeToggle />

        <Button
          variant="outline"
          size="sm"
          onClick={handleSignOut}
          data-testid="logout-btn"
        >
          Sign Out
        </Button>
      </div>
    </header>
  );
};
