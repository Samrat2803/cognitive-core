import { BarChart3, History, Settings } from 'lucide-react';
import ConnectionStatus from '../ui/ConnectionStatus';
import './Header.css';

export function Header() {
  return (
    <header className="header">
      <div className="header-left">
        <BarChart3 size={24} className="logo-icon" />
        <h1 className="header-title">Political Analyst Workbench</h1>
      </div>
      <div className="header-right">
        <ConnectionStatus />
        <button className="header-button" title="History">
          <History size={20} />
        </button>
        <button className="header-button" title="Settings">
          <Settings size={20} />
        </button>
      </div>
    </header>
  );
}

