import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    // Update state so the next render shows the fallback UI.
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // You can log the error to a reporting service here
    console.error("❌ Uncaught error in component tree:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <div 
              className="max-w-2xl w-full p-8 rounded-lg"
              style={{ 
                backgroundColor: '#381E1E', 
                border: '1px solid #FF444450' 
              }}
            >
              <h1 
                className="text-2xl font-light mb-2"
                style={{ color: '#FFB8B8' }}
              >
                Something went wrong
              </h1>
              <p 
                className="mb-4"
                style={{ color: '#FFD1D1' }}
              >
                A rendering error occurred. Check the browser's developer console for more details.
              </p>
              <pre 
                className="p-4 rounded-md text-sm overflow-x-auto"
                style={{ 
                  backgroundColor: '#1a0000', 
                  color: '#FFB8B8',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-all'
                }}
              >
                {this.state.error?.toString()}
              </pre>
            </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;