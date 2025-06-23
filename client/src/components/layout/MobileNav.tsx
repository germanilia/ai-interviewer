import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  Users,
  Settings,
  UserCheck,
  MessageSquare,
  HelpCircle,
  Briefcase,
  BarChart3
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { 
  Sheet, 
  SheetContent, 
  SheetHeader, 
  SheetTitle 
} from '@/components/ui/sheet';
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
    title: 'Candidates',
    href: '/candidates',
    icon: UserCheck,
  },
  {
    title: 'Interviews',
    href: '/interviews',
    icon: MessageSquare,
  },
  {
    title: 'Questions',
    href: '/questions',
    icon: HelpCircle,
  },
  {
    title: 'Jobs',
    href: '/job-positions',
    icon: Briefcase,
  },
  {
    title: 'Reports',
    href: '/reports',
    icon: BarChart3,
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

export const MobileNav: React.FC = () => {
  const { isOpen, close } = useSidebar();
  const { user } = useAuth();
  const location = useLocation();

  const filteredNavItems = navItems.filter(item => 
    !item.adminOnly || user?.role === 'admin'
  );

  return (
    <Sheet open={isOpen} onOpenChange={(open) => !open && close()}>
      <SheetContent side="left" className="w-64 p-0" data-testid="mobile-overlay">
        <SheetHeader className="p-4 border-b border-border">
          <SheetTitle className="flex items-center justify-start">
            <Logo width={120} height={32} className="h-8" />
          </SheetTitle>
        </SheetHeader>
        
        <nav className="flex-1 space-y-1 p-2">
          {filteredNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href;
            
            // Generate test ID from href, keeping the structure readable
            const testId = `nav-${item.href.replace('/', '').replace(/-/g, '')}`;

            return (
              <Link
                key={item.href}
                to={item.href}
                onClick={close}
                data-testid={testId}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
                  isActive
                    ? "bg-accent text-accent-foreground active"
                    : "text-muted-foreground"
                )}
                aria-current={isActive ? "page" : undefined}
              >
                <Icon className="h-4 w-4 flex-shrink-0" />
                <span>{item.title}</span>
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto">
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
        </div>
      </SheetContent>
    </Sheet>
  );
};
