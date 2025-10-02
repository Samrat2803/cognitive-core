import { useLocation } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';

interface LocationState {
  initialQuery?: string;
}

export function ChatPage() {
  const location = useLocation();
  const state = location.state as LocationState;
  const initialQuery = state?.initialQuery;

  return <MainLayout initialQuery={initialQuery} />;
}

