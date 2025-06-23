import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  Users,
  Settings,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Logo } from '@/components/ui/logo';
import { useSidebar } from '@/contexts/SidebarContext';
import { useAuth } from '@/contexts/AuthContext';

interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  adminOnly?: boolean;
}

const navItems: NavItem[] = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: Home,
  },
  {
    title: 'Users',
    href: '/users',
    icon: Users,
    adminOnly: true,
  },
  {
    title: 'Settings',
    href: '/settings',
    icon: Settings,
  },
];

interface SidebarProps {
  className?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ className }) => {
  const { isOpen, toggle, isMobile } = useSidebar();
  const { user } = useAuth();
  const location = useLocation();

  const filteredNavItems = navItems.filter(item => 
    !item.adminOnly || user?.role === 'admin'
  );

  return (
    <div
      className={cn(
        "relative flex h-full flex-col bg-card border-r border-border transition-all duration-300",
        isOpen ? "w-64" : "w-16",
        className
      )}
    >
      {/* Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-border">
        {isOpen && (
          <Logo width={120} height={32} className="h-8" />
        )}
        {!isMobile && (
          <Button
            variant="ghost"
            size="icon"
            onClick={toggle}
            className="h-8 w-8"
          >
            {isOpen ? (
              <ChevronLeft className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </Button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-2">
        {filteredNavItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.href;
          
          return (
            <Link
              key={item.href}
              to={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
                isActive 
                  ? "bg-accent text-accent-foreground" 
                  : "text-muted-foreground",
                !isOpen && "justify-center px-2"
              )}
              title={!isOpen ? item.title : undefined}
            >
              <Icon className="h-4 w-4 flex-shrink-0" />
              {isOpen && <span>{item.title}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      {isOpen && (
        <>
          <Separator />
          <div className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                <span className="text-xs font-medium text-primary">
                  {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground truncate">
                  {user?.full_name || user?.email}
                </p>
                <p className="text-xs text-muted-foreground capitalize">
                  {user?.role}
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
