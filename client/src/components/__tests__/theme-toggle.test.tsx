import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { ThemeToggle } from '@/components/ui/theme-toggle';

const ThemeToggleWithProvider = () => (
  <ThemeProvider>
    <ThemeToggle />
  </ThemeProvider>
);

describe('ThemeToggle', () => {
  beforeEach(() => {
    // Clear mocks and reset DOM
    jest.clearAllMocks();
    document.documentElement.className = '';
    (localStorage.getItem as jest.Mock).mockReturnValue(null);
  });

  it('renders theme toggle button', () => {
    render(<ThemeToggleWithProvider />);
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
  });

  it('cycles through themes when clicked', () => {
    render(<ThemeToggleWithProvider />);
    const button = screen.getByRole('button');

    // Initial state should be system (Monitor icon)
    expect(button).toHaveAttribute('title', 'Switch to light mode');

    // Click to go to light mode
    fireEvent.click(button);
    expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'light');

    // Click to go to dark mode
    fireEvent.click(button);
    expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'dark');

    // Click to go back to system mode
    fireEvent.click(button);
    expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'system');
  });

  it('applies theme class to document element', () => {
    render(<ThemeToggleWithProvider />);
    const button = screen.getByRole('button');

    // Click to set light theme
    fireEvent.click(button);
    expect(document.documentElement.classList.contains('light')).toBe(true);

    // Click to set dark theme
    fireEvent.click(button);
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('loads saved theme from localStorage', () => {
    (localStorage.getItem as jest.Mock).mockReturnValue('dark');
    
    render(<ThemeToggleWithProvider />);
    
    // Should apply dark theme on load
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('respects system preference when theme is system', () => {
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

    render(<ThemeToggleWithProvider />);
    
    // Should apply dark theme based on system preference
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });
});
