import { useWebSocket } from '../../hooks/useWebSocket';
import './ConnectionStatus.css';

/**
 * Connection Status Indicator
 * Shows WebSocket connection state with icon and tooltip
 */
function ConnectionStatus() {
  const { status, isConnected, connect } = useWebSocket();

  const getStatusIcon = () => {
    switch (status) {
      case 'connected':
        return '🟢';
      case 'connecting':
        return '🟡';
      case 'disconnected':
        return '⚪';
      case 'error':
        return '🔴';
      default:
        return '⚪';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'connected':
        return 'Connected';
      case 'connecting':
        return 'Connecting...';
      case 'disconnected':
        return 'Disconnected';
      case 'error':
        return 'Connection Error';
      default:
        return 'Unknown';
    }
  };

  const handleClick = () => {
    if (!isConnected) {
      connect();
    }
  };

  return (
    <div 
      className={`connection-status ${status}`}
      onClick={handleClick}
      title={getStatusText()}
    >
      <span className="status-icon">{getStatusIcon()}</span>
      <span className="status-text">{getStatusText()}</span>
      {!isConnected && (
        <button className="reconnect-btn" onClick={handleClick}>
          Reconnect
        </button>
      )}
    </div>
  );
}

export default ConnectionStatus;

