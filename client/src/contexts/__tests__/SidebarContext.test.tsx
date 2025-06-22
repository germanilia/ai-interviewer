import { render, screen, act, fireEvent } from '@testing-library/react';
import { SidebarProvider, useSidebar } from '@/contexts/SidebarContext';

// Test component to access the sidebar context
const TestComponent = () => {
  const { isOpen, isMobile, toggle, open, close } = useSidebar();
  
  return (
    <div>
      <div data-testid="is-open">{isOpen ? 'open' : 'closed'}</div>
      <div data-testid="is-mobile">{isMobile ? 'mobile' : 'desktop'}</div>
      <button onClick={toggle} data-testid="toggle">
        Toggle
      </button>
      <button onClick={open} data-testid="open">
        Open
      </button>
      <button onClick={close} data-testid="close">
        Close
      </button>
    </div>
  );
};

const renderWithSidebarProvider = () => {
  return render(
    <SidebarProvider>
      <TestComponent />
    </SidebarProvider>
  );
};

// Helper to simulate window resize
const simulateResize = (width: number) => {
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: width,
  });
  
  fireEvent(window, new Event('resize'));
};

describe('SidebarContext', () => {
  const originalInnerWidth = window.innerWidth;

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    
    // Make sure localStorage.getItem returns null, not undefined
    (localStorage.getItem as jest.Mock).mockReturnValue(null);
    
    // Reset window size to desktop
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024,
    });
  });

  afterEach(() => {
    // Restore original window width
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: originalInnerWidth,
    });
  });

  describe('initialization', () => {
    it('starts with open sidebar and detects desktop', () => {
      renderWithSidebarProvider();
      
      expect(screen.getByTestId('is-open')).toHaveTextContent('open');
      expect(screen.getByTestId('is-mobile')).toHaveTextContent('desktop');
    });

    it('detects mobile viewport', () => {
      simulateResize(500);
      
      renderWithSidebarProvider();
      
      expect(screen.getByTestId('is-mobile')).toHaveTextContent('mobile');
    });

    it('loads saved sidebar state on desktop', () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('true');
      
      renderWithSidebarProvider();
      
      expect(screen.getByTestId('is-open')).toHaveTextContent('open');
    });

    it('ignores saved state on mobile', () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('true');
      simulateResize(500);
      
      renderWithSidebarProvider();
      
      expect(screen.getByTestId('is-open')).toHaveTextContent('closed');
    });
  });

  describe('responsive behavior', () => {
    it('switches to mobile when resizing below 768px', () => {
      renderWithSidebarProvider();
      
      expect(screen.getByTestId('is-mobile')).toHaveTextContent('desktop');
      
      act(() => {
        simulateResize(500);
      });
      
      expect(screen.getByTestId('is-mobile')).toHaveTextContent('mobile');
    });

    it('switches to desktop when resizing above 768px', () => {
      simulateResize(500);
      renderWithSidebarProvider();
      
      expect(screen.getByTestId('is-mobile')).toHaveTextContent('mobile');
      
      act(() => {
        simulateResize(1024);
      });
      
      expect(screen.getByTestId('is-mobile')).toHaveTextContent('desktop');
    });

    it('closes sidebar when switching from desktop to mobile', () => {
      renderWithSidebarProvider();
      
      // Open sidebar on desktop
      act(() => {
        screen.getByTestId('open').click();
      });
      
      expect(screen.getByTestId('is-open')).toHaveTextContent('open');
      
      // Resize to mobile
      act(() => {
        simulateResize(500);
      });
      
      expect(screen.getByTestId('is-open')).toHaveTextContent('closed');
    });

    it('loads saved state when switching from mobile to desktop', () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('true');
      simulateResize(500);
      renderWithSidebarProvider();
      
      expect(screen.getByTestId('is-open')).toHaveTextContent('closed');
      
      // Resize to desktop
      act(() => {
        simulateResize(1024);
      });
      
      expect(screen.getByTestId('is-open')).toHaveTextContent('open');
    });
  });

  describe('sidebar controls', () => {
    it('toggles sidebar state', () => {
      renderWithSidebarProvider();
      
      expect(screen.getByTestId('is-open')).toHaveTextContent('open');
      
      act(() => {
        screen.getByTestId('toggle').click();
      });
      
      expect(screen.getByTestId('is-open')).toHaveTextContent('closed');
      
      act(() => {
        screen.getByTestId('toggle').click();
      });
      
      expect(screen.getByTestId('is-open')).toHaveTextContent('open');
    });

    it('opens sidebar', () => {
      renderWithSidebarProvider();
      
      // First close the sidebar (it starts open)
      act(() => {
        screen.getByTestId('close').click();
      });
      
      expect(screen.getByTestId('is-open')).toHaveTextContent('closed');
      
      act(() => {
        screen.getByTestId('open').click();
      });
      
      expect(screen.getByTestId('is-open')).toHaveTextContent('open');
    });

    it('closes sidebar', () => {
      renderWithSidebarProvider();
      
      // First open it
      act(() => {
        screen.getByTestId('open').click();
      });
      
      expect(screen.getByTestId('is-open')).toHaveTextContent('open');
      
      act(() => {
        screen.getByTestId('close').click();
      });
      
      expect(screen.getByTestId('is-open')).toHaveTextContent('closed');
    });
  });

  describe('localStorage persistence', () => {
    it('saves sidebar state to localStorage on desktop', () => {
      renderWithSidebarProvider();
      
      act(() => {
        screen.getByTestId('open').click();
      });
      
      expect(localStorage.setItem).toHaveBeenCalledWith('sidebar-open', 'true');
      
      act(() => {
        screen.getByTestId('close').click();
      });
      
      expect(localStorage.setItem).toHaveBeenCalledWith('sidebar-open', 'false');
    });

    it('does not save state to localStorage on mobile', () => {
      simulateResize(500);
      renderWithSidebarProvider();
      
      act(() => {
        screen.getByTestId('toggle').click();
      });
      
      expect(localStorage.setItem).not.toHaveBeenCalled();
    });
  });

  describe('error handling', () => {
    it('throws error when useSidebar is used outside SidebarProvider', () => {
      // Mock console.error to avoid test output noise
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      expect(() => {
        render(<TestComponent />);
      }).toThrow('useSidebar must be used within a SidebarProvider');
      
      consoleSpy.mockRestore();
    });
  });

  describe('cleanup', () => {
    it('removes resize event listener on unmount', () => {
      const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener');
      
      const { unmount } = renderWithSidebarProvider();
      
      unmount();
      
      expect(removeEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function));
      
      removeEventListenerSpy.mockRestore();
    });
  });
});
