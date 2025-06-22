import React from 'react';
import { SidebarProvider, useSidebar } from '@/contexts/SidebarContext';
import { Sidebar } from './Sidebar';
import { MobileNav } from './MobileNav';
import { Header } from './Header';
import { cn } from '@/lib/utils';

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayoutContent: React.FC<AppLayoutProps> = ({ children }) => {
  const { isOpen, isMobile } = useSidebar();

  return (
    <div className="min-h-screen bg-background">
      {/* Desktop Sidebar */}
      {!isMobile && (
        <aside className="fixed left-0 top-0 z-40 h-full">
          <Sidebar />
        </aside>
      )}

      {/* Mobile Navigation */}
      {isMobile && <MobileNav />}

      {/* Main Content Area */}
      <div
        className={cn(
          "flex flex-col transition-all duration-300",
          !isMobile && isOpen && "ml-64",
          !isMobile && !isOpen && "ml-16"
        )}
      >
        {/* Header */}
        <Header />

        {/* Page Content */}
        <main className="flex-1 p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <SidebarProvider>
      <AppLayoutContent>{children}</AppLayoutContent>
    </SidebarProvider>
  );
};
