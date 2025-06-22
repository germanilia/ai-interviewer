import { cn } from '@/lib/utils';

describe('cn utility function', () => {
  it('merges class names correctly', () => {
    const result = cn('class1', 'class2');
    expect(result).toBe('class1 class2');
  });

  it('handles conditional classes', () => {
    const result = cn('base-class', true && 'conditional-class', false && 'hidden-class');
    expect(result).toBe('base-class conditional-class');
  });

  it('handles Tailwind CSS class conflicts', () => {
    // Test that tailwind-merge resolves conflicts
    const result = cn('p-4', 'p-2');
    expect(result).toBe('p-2'); // Latest padding class wins
  });

  it('handles multiple conflicting classes', () => {
    const result = cn('bg-red-500', 'bg-blue-500', 'text-white');
    expect(result).toBe('bg-blue-500 text-white');
  });

  it('handles undefined and null values', () => {
    const result = cn('class1', undefined, null, 'class2');
    expect(result).toBe('class1 class2');
  });

  it('handles empty strings', () => {
    const result = cn('class1', '', 'class2');
    expect(result).toBe('class1 class2');
  });

  it('handles arrays of classes', () => {
    const result = cn(['class1', 'class2'], 'class3');
    expect(result).toBe('class1 class2 class3');
  });

  it('handles object notation for conditional classes', () => {
    const result = cn({
      'base-class': true,
      'active-class': true,
      'inactive-class': false,
    });
    expect(result).toBe('base-class active-class');
  });

  it('handles complex combinations', () => {
    const isActive = true;
    const hasError = false;
    const size = 'large';
    
    const result = cn(
      'base-button',
      {
        'button-active': isActive,
        'button-error': hasError,
      },
      size === 'large' && 'button-large',
      'text-white'
    );
    
    expect(result).toBe('base-button button-active button-large text-white');
  });

  it('resolves responsive class conflicts', () => {
    const result = cn('text-sm', 'md:text-base', 'lg:text-lg', 'md:text-xl');
    // Should keep both responsive variants but resolve conflicts within same breakpoint
    expect(result).toContain('text-sm');
    expect(result).toContain('lg:text-lg');
    expect(result).toContain('md:text-xl');
    expect(result).not.toContain('md:text-base');
  });

  it('handles modifier classes correctly', () => {
    const result = cn('hover:bg-red-500', 'hover:bg-blue-500', 'focus:ring-2');
    expect(result).toBe('hover:bg-blue-500 focus:ring-2');
  });

  it('returns empty string for no valid classes', () => {
    const result = cn(undefined, null, false, '');
    expect(result).toBe('');
  });

  it('handles very long class lists', () => {
    const classes = Array.from({ length: 100 }, (_, i) => `class-${i}`);
    const result = cn(...classes);
    
    expect(result).toContain('class-0');
    expect(result).toContain('class-99');
    expect(result.split(' ')).toHaveLength(100);
  });

  it('preserves important modifiers', () => {
    const result = cn('!text-red-500', 'text-blue-500');
    expect(result).toBe('!text-red-500 text-blue-500');
  });

  it('handles arbitrary values in Tailwind classes', () => {
    const result = cn('text-[14px]', 'text-[16px]', 'bg-[#ff0000]');
    expect(result).toBe('text-[16px] bg-[#ff0000]');
  });
});
