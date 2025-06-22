import { render, screen, act } from '@testing-library/react';
import { ThemeProvider, useTheme } from '@/contexts/ThemeContext';

// Test component to access the theme context
const TestComponent = () => {
  const { theme, setTheme } = useTheme();
  
  return (
    <div>
      <div data-testid="theme">{theme}</div>
      <button onClick={() => setTheme('light')} data-testid="set-light">
        Set Light
      </button>
      <button onClick={() => setTheme('dark')} data-testid="set-dark">
        Set Dark
      </button>
      <button onClick={() => setTheme('system')} data-testid="set-system">
        Set System
      </button>
    </div>
  );
};

const renderWithThemeProvider = () => {
  return render(
    <ThemeProvider>
      <TestComponent />
    </ThemeProvider>
  );
};

describe('ThemeContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    document.documentElement.className = '';
    
    // Reset matchMedia mock
    (window.matchMedia as jest.Mock).mockImplementation((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }));
  });

  describe('initialization', () => {
    it('defaults to system theme when no stored preference', () => {
      (localStorage.getItem as jest.Mock).mockReturnValue(null);
      
      renderWithThemeProvider();
      
      expect(screen.getByTestId('theme')).toHaveTextContent('system');
    });

    it('loads stored theme preference', () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('dark');
      
      renderWithThemeProvider();
      
      expect(screen.getByTestId('theme')).toHaveTextContent('dark');
    });

    it('applies light theme class when theme is light', () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('light');
      
      renderWithThemeProvider();
      
      expect(document.documentElement.classList.contains('light')).toBe(true);
      expect(document.documentElement.classList.contains('dark')).toBe(false);
    });

    it('applies dark theme class when theme is dark', () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('dark');
      
      renderWithThemeProvider();
      
      expect(document.documentElement.classList.contains('dark')).toBe(true);
      expect(document.documentElement.classList.contains('light')).toBe(false);
    });

    it('applies system preference when theme is system and prefers dark', () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('system');
      (window.matchMedia as jest.Mock).mockImplementation((query: string) => ({
        matches: query === '(prefers-color-scheme: dark)',
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      }));
      
      renderWithThemeProvider();
      
      expect(document.documentElement.classList.contains('dark')).toBe(true);
    });

    it('applies light theme when theme is system and prefers light', () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('system');
      (window.matchMedia as jest.Mock).mockImplementation((query: string) => ({
        matches: query === '(prefers-color-scheme: light)',
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      }));
      
      renderWithThemeProvider();
      
      expect(document.documentElement.classList.contains('light')).toBe(true);
    });
  });

  describe('theme switching', () => {
    it('switches to light theme and saves to localStorage', () => {
      renderWithThemeProvider();
      
      act(() => {
        screen.getByTestId('set-light').click();
      });
      
      expect(screen.getByTestId('theme')).toHaveTextContent('light');
      expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'light');
      expect(document.documentElement.classList.contains('light')).toBe(true);
    });

    it('switches to dark theme and saves to localStorage', () => {
      renderWithThemeProvider();
      
      act(() => {
        screen.getByTestId('set-dark').click();
      });
      
      expect(screen.getByTestId('theme')).toHaveTextContent('dark');
      expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'dark');
      expect(document.documentElement.classList.contains('dark')).toBe(true);
    });

    it('switches to system theme and saves to localStorage', () => {
      renderWithThemeProvider();
      
      act(() => {
        screen.getByTestId('set-system').click();
      });
      
      expect(screen.getByTestId('theme')).toHaveTextContent('system');
      expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'system');
    });

    it('removes previous theme classes when switching', () => {
      renderWithThemeProvider();
      
      // Set to light theme first
      act(() => {
        screen.getByTestId('set-light').click();
      });
      
      expect(document.documentElement.classList.contains('light')).toBe(true);
      
      // Switch to dark theme
      act(() => {
        screen.getByTestId('set-dark').click();
      });
      
      expect(document.documentElement.classList.contains('light')).toBe(false);
      expect(document.documentElement.classList.contains('dark')).toBe(true);
    });
  });

  describe('system theme changes', () => {
    it('responds to system theme changes when theme is system', () => {
      // Set up the mock to return system theme initially
      (localStorage.getItem as jest.Mock).mockReturnValue('system');

      let mediaQueryCallback: ((e: MediaQueryListEvent) => void) | null = null;
      let mockMatches = false;

      (window.matchMedia as jest.Mock).mockImplementation((query: string) => ({
        get matches() { return mockMatches; },
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn((event: string, callback: (e: MediaQueryListEvent) => void) => {
          if (event === 'change') {
            mediaQueryCallback = callback;
          }
        }),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      }));

      renderWithThemeProvider();

      // Verify we start in system mode with light theme
      expect(document.documentElement.classList.contains('light')).toBe(true);
      expect(document.documentElement.classList.contains('dark')).toBe(false);

      // Simulate system theme change to dark
      if (mediaQueryCallback) {
        act(() => {
          mockMatches = true; // Update the mock to return dark theme
          mediaQueryCallback!({ matches: true } as MediaQueryListEvent);
        });

        expect(document.documentElement.classList.contains('dark')).toBe(true);
        expect(document.documentElement.classList.contains('light')).toBe(false);
      } else {
        // If callback wasn't set, fail the test with a helpful message
        fail('Media query callback was not set up properly');
      }
    });
  });

  describe('error handling', () => {
    it('throws error when useTheme is used outside ThemeProvider', () => {
      // Mock console.error to avoid test output noise
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      expect(() => {
        render(<TestComponent />);
      }).toThrow('useTheme must be used within a ThemeProvider');
      
      consoleSpy.mockRestore();
    });
  });

  describe('cleanup', () => {
    it('removes event listeners on unmount', () => {
      const removeEventListenerSpy = jest.fn();
      
      (window.matchMedia as jest.Mock).mockImplementation(() => ({
        matches: false,
        media: '',
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: removeEventListenerSpy,
        dispatchEvent: jest.fn(),
      }));
      
      const { unmount } = renderWithThemeProvider();
      
      unmount();
      
      expect(removeEventListenerSpy).toHaveBeenCalled();
    });
  });
});
