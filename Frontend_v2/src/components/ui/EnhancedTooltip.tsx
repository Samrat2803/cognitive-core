import React, { useState, useRef, useEffect } from 'react';
import { Info, Zap, Brain, Search, BarChart3 } from 'lucide-react';
import './EnhancedTooltip.css';

export type TooltipIcon = 'info' | 'agent' | 'feature' | 'search' | 'chart' | 'none';
export type TooltipPosition = 'top' | 'bottom' | 'left' | 'right';

interface EnhancedTooltipProps {
  children: React.ReactNode;
  content: string | React.ReactNode;
  icon?: TooltipIcon;
  position?: TooltipPosition;
  delay?: number;
  maxWidth?: number;
  showArrow?: boolean;
  disabled?: boolean;
}

const DEFAULT_MAX_WIDTH = 340; // Optimal for readability

export function EnhancedTooltip({
  children,
  content,
  icon = 'none',
  position = 'top',
  delay = 300,
  maxWidth = DEFAULT_MAX_WIDTH,
  showArrow = true,
  disabled = false,
}: EnhancedTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [coords, setCoords] = useState({ x: 0, y: 0 });
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  const showTooltip = () => {
    if (disabled) return;
    
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
      updatePosition();
    }, delay);
  };

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };

  const updatePosition = () => {
    if (!triggerRef.current || !tooltipRef.current) return;

    const rect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const scrollX = window.scrollX || window.pageXOffset;
    const scrollY = window.scrollY || window.pageYOffset;
    
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const padding = 16; // Minimum distance from viewport edges

    let x = 0;
    let y = 0;

    switch (position) {
      case 'top':
        x = rect.left + rect.width / 2 + scrollX;
        y = rect.top + scrollY;
        break;
      case 'bottom':
        x = rect.left + rect.width / 2 + scrollX;
        y = rect.bottom + scrollY;
        break;
      case 'left':
        x = rect.left + scrollX;
        y = rect.top + rect.height / 2 + scrollY;
        break;
      case 'right':
        x = rect.right + scrollX;
        y = rect.top + rect.height / 2 + scrollY;
        break;
    }

    // Prevent tooltip from going off-screen horizontally
    const tooltipWidth = tooltipRect.width || maxWidth;
    if (position === 'top' || position === 'bottom') {
      const halfWidth = tooltipWidth / 2;
      // Check if tooltip would go off right edge
      if (x + halfWidth > viewportWidth - padding) {
        x = viewportWidth - halfWidth - padding;
      }
      // Check if tooltip would go off left edge
      if (x - halfWidth < padding) {
        x = halfWidth + padding;
      }
    } else if (position === 'right') {
      // Check if tooltip would go off right edge
      if (x + tooltipWidth > viewportWidth - padding) {
        x = viewportWidth - tooltipWidth - padding;
      }
    } else if (position === 'left') {
      // Check if tooltip would go off left edge
      if (x - tooltipWidth < padding) {
        x = tooltipWidth + padding;
      }
    }

    // Prevent tooltip from going off-screen vertically
    const tooltipHeight = tooltipRect.height || 100;
    if (position === 'left' || position === 'right') {
      const halfHeight = tooltipHeight / 2;
      // Check if tooltip would go off bottom
      if (y + halfHeight > viewportHeight - padding) {
        y = viewportHeight - halfHeight - padding;
      }
      // Check if tooltip would go off top
      if (y - halfHeight < padding) {
        y = halfHeight + padding;
      }
    }

    setCoords({ x, y });
  };

  useEffect(() => {
    if (isVisible) {
      updatePosition();
      window.addEventListener('scroll', updatePosition);
      window.addEventListener('resize', updatePosition);

      return () => {
        window.removeEventListener('scroll', updatePosition);
        window.removeEventListener('resize', updatePosition);
      };
    }
  }, [isVisible]);

  const getIcon = () => {
    switch (icon) {
      case 'info':
        return <Info size={14} />;
      case 'agent':
        return <Brain size={14} />;
      case 'feature':
        return <Zap size={14} />;
      case 'search':
        return <Search size={14} />;
      case 'chart':
        return <BarChart3 size={14} />;
      default:
        return null;
    }
  };

  return (
    <>
      <div
        ref={triggerRef}
        className="tooltip-trigger"
        onMouseEnter={showTooltip}
        onMouseLeave={hideTooltip}
        onFocus={showTooltip}
        onBlur={hideTooltip}
      >
        {children}
      </div>

      {isVisible && (
        <div
          ref={tooltipRef}
          className={`enhanced-tooltip enhanced-tooltip-${position} ${icon !== 'none' ? 'has-icon' : ''}`}
          style={{
            left: `${coords.x}px`,
            top: `${coords.y}px`,
            maxWidth: `${maxWidth}px`,
          }}
        >
          <div className="tooltip-content">
            {icon !== 'none' && (
              <div className={`tooltip-icon tooltip-icon-${icon}`}>
                {getIcon()}
              </div>
            )}
            <div className="tooltip-text">{content}</div>
          </div>
          {showArrow && <div className="tooltip-arrow" />}
        </div>
      )}
    </>
  );
}

// Specialized tooltip for agent features
interface AgentTooltipProps {
  children: React.ReactNode;
  title: string;
  description: string;
  features?: string[];
  position?: TooltipPosition;
}

export function AgentTooltip({
  children,
  title,
  description,
  features,
  position = 'top',
}: AgentTooltipProps) {
  const content = (
    <div className="agent-tooltip-content">
      <div className="agent-tooltip-header">
        <Brain size={16} className="agent-icon" />
        <strong>{title}</strong>
      </div>
      <p className="agent-tooltip-description">{description}</p>
      {features && features.length > 0 && (
        <ul className="agent-tooltip-features">
          {features.map((feature, idx) => (
            <li key={idx}>
              <Zap size={12} />
              {feature}
            </li>
          ))}
        </ul>
      )}
    </div>
  );

  return (
    <EnhancedTooltip
      content={content}
      icon="none"
      position={position}
      maxWidth={380}
      delay={200}
    >
      {children}
    </EnhancedTooltip>
  );
}

// Feature badge with tooltip
interface FeatureBadgeProps {
  label: string;
  tooltip: string;
  icon?: TooltipIcon;
  variant?: 'primary' | 'secondary' | 'accent';
}

export function FeatureBadge({
  label,
  tooltip,
  icon = 'feature',
  variant = 'primary',
}: FeatureBadgeProps) {
  return (
    <EnhancedTooltip content={tooltip} icon={icon} position="top">
      <span className={`feature-badge feature-badge-${variant}`}>
        {label}
      </span>
    </EnhancedTooltip>
  );
}

