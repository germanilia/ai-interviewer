import { useToast } from "@/hooks/use-toast"
import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from "@/components/ui/toast"

export function Toaster() {
  const { toasts } = useToast()

  return (
    <ToastProvider>
      {toasts.map(function ({ id, title, description, action, variant, ...props }) {
        // Determine test ID based on variant
        const getTestId = () => {
          if (variant === 'destructive') return 'error-toast';
          if (title === 'Success') return 'success-toast';
          if (title === 'Warning') return 'warning-toast';
          if (title === 'Info') return 'info-toast';
          return 'toast';
        };

        return (
          <Toast key={id} variant={variant} data-testid={getTestId()} {...props}>
            <div className="grid gap-1">
              {title && <ToastTitle>{title}</ToastTitle>}
              {description && (
                <ToastDescription>{description}</ToastDescription>
              )}
            </div>
            {action}
            <ToastClose />
          </Toast>
        )
      })}
      <ToastViewport />
    </ToastProvider>
  )
}
