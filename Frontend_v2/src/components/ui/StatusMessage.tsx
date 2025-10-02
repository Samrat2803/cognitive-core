import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import './StatusMessage.css';

export type StatusType = 'loading' | 'complete' | 'error';

interface StatusMessageProps {
  message: string;
  type?: StatusType;
  step?: string;
}

export function StatusMessage({ message, type = 'loading', step }: StatusMessageProps) {
  return (
    <div className={`status-message status-${type}`}>
      <div className="status-icon">
        {type === 'loading' && <Loader2 size={16} className="animate-spin" />}
        {type === 'complete' && <CheckCircle size={16} />}
        {type === 'error' && <AlertCircle size={16} />}
      </div>
      <div className="status-content">
        {step && <span className="status-step">{step}</span>}
        <span className="status-text">{message}</span>
      </div>
    </div>
  );
}

