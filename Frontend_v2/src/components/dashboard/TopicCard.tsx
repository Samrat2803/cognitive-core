import React from 'react';

interface Topic {
  rank: number;
  topic: string;
  explosiveness_score: number;
  classification: string;
  frequency: number;
  image_url?: string;
  entities?: {
    people?: string[];
    countries?: string[];
    organizations?: string[];
  };
  reasoning: string;
}

interface TopicCardProps {
  topic: Topic;
  onClick: () => void;
}

export function TopicCard({ topic, onClick }: TopicCardProps) {
  // Determine color based on classification - Subtle Professional
  const getColorClasses = (classification: string) => {
    if (classification.includes('CRITICAL')) {
      return {
        bg: 'linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(99, 102, 241, 0.08) 100%)',
        border: 'rgba(139, 92, 246, 0.4)',
        badge: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
        text: '#a78bfa',
        glow: 'rgba(139, 92, 246, 0.2)'
      };
    }
    if (classification.includes('EXPLOSIVE')) {
      return {
        bg: 'linear-gradient(135deg, rgba(217, 243, 120, 0.08) 0%, rgba(163, 230, 53, 0.08) 100%)',
        border: 'rgba(217, 243, 120, 0.4)',
        badge: 'linear-gradient(135deg, #d9f378 0%, #a3e635 100%)',
        text: '#d9f378',
        glow: 'rgba(217, 243, 120, 0.2)'
      };
    }
    if (classification.includes('TRENDING')) {
      return {
        bg: 'linear-gradient(135deg, rgba(96, 165, 250, 0.08) 0%, rgba(59, 130, 246, 0.08) 100%)',
        border: 'rgba(96, 165, 250, 0.4)',
        badge: 'linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%)',
        text: '#93c5fd',
        glow: 'rgba(96, 165, 250, 0.2)'
      };
    }
    return {
      bg: 'linear-gradient(135deg, rgba(148, 163, 184, 0.08) 0%, rgba(100, 116, 139, 0.08) 100%)',
      border: 'rgba(148, 163, 184, 0.4)',
      badge: 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)',
      text: '#cbd5e1',
      glow: 'rgba(148, 163, 184, 0.2)'
    };
  };

  const colors = getColorClasses(topic.classification);

  return (
    <div 
      className="topic-card"
      onClick={onClick}
      style={{
        background: colors.bg,
        border: `1px solid ${colors.border}`,
        borderRadius: '8px',
        padding: topic.image_url ? '0' : '1rem',
        height: topic.image_url ? '280px' : '220px',
        display: 'flex',
        flexDirection: 'column',
        cursor: 'pointer',
        transition: 'all 0.3s ease',
        position: 'relative',
        overflow: 'hidden',
        backdropFilter: 'blur(10px)'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.boxShadow = `0 8px 24px ${colors.glow}`;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      {/* Image (if available) */}
      {topic.image_url && (
        <div 
          style={{
            width: '100%',
            height: '110px',
            overflow: 'hidden',
            borderRadius: '8px 8px 0 0',
            position: 'relative',
            background: 'rgba(255,255,255,0.03)',
            flexShrink: 0
          }}
        >
          <img 
            src={topic.image_url} 
            alt={topic.topic}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              filter: 'brightness(0.9) contrast(1.1)'
            }}
            onError={(e) => {
              // Hide image container if it fails to load
              const parent = e.currentTarget.parentElement;
              if (parent) parent.style.display = 'none';
            }}
          />
          {/* Gradient overlay for better text readability */}
          <div 
            style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              height: '50%',
              background: 'linear-gradient(to top, rgba(0,0,0,0.6), transparent)'
            }}
          />
        </div>
      )}

      {/* Content wrapper with padding */}
      <div style={{ padding: topic.image_url ? '1rem' : '0', flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Rank Badge */}
        <div 
          style={{
            position: 'absolute',
            top: topic.image_url ? '80px' : '8px',
            left: '8px',
            background: colors.badge,
            color: '#1c1e20',
            fontWeight: 700,
            fontSize: '0.7rem',
            padding: '3px 7px',
            borderRadius: '4px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.4)',
            zIndex: 10
          }}
        >
          #{topic.rank}
        </div>

        {/* Emoji */}
        <div 
          style={{
            position: 'absolute',
            top: topic.image_url ? '80px' : '8px',
            right: '8px',
            fontSize: '1.2rem',
            zIndex: 10,
            textShadow: topic.image_url ? '0 2px 4px rgba(0,0,0,0.5)' : 'none'
          }}
        >
          {topic.classification.split(' ')[0]}
        </div>

        {/* Title */}
        <h3 
          style={{
            color: colors.text,
            fontWeight: 700,
            fontSize: '0.9rem',
            marginTop: topic.image_url ? '0rem' : '2.2rem',
            marginBottom: '0.75rem',
            lineHeight: '1.3',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            minHeight: '2.6rem'
          }}
        >
          {topic.topic}
        </h3>

      {/* Metrics */}
      <div style={{ display: 'flex', gap: '0.4rem', marginBottom: '0.75rem' }}>
        <span 
          style={{
            background: colors.badge,
            color: '#1c1e20',
            fontSize: '0.7rem',
            fontWeight: 700,
            padding: '3px 8px',
            borderRadius: '4px'
          }}
        >
          {topic.explosiveness_score}/100
        </span>
        <span 
          style={{
            background: 'rgba(255,255,255,0.08)',
            color: '#ccc',
            fontSize: '0.7rem',
            padding: '3px 8px',
            borderRadius: '4px',
            border: '1px solid rgba(255,255,255,0.1)'
          }}
        >
          {topic.frequency} articles
        </span>
      </div>

      {/* Entities */}
      {topic.entities && (
        <div style={{ fontSize: '0.7rem', color: '#ccc', marginBottom: '0.75rem' }}>
          {topic.entities.people && topic.entities.people.length > 0 && (
            <div style={{ marginBottom: '3px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              👤 {topic.entities.people.slice(0, 2).join(', ')}
            </div>
          )}
          {topic.entities.countries && topic.entities.countries.length > 0 && (
            <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              🌍 {topic.entities.countries.slice(0, 2).join(', ')}
            </div>
          )}
        </div>
      )}

      {/* Reasoning */}
      <p 
        style={{
          fontSize: '0.7rem',
          color: '#aaa',
          lineHeight: '1.3',
          marginTop: 'auto',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
          textOverflow: 'ellipsis'
        }}
      >
        {topic.reasoning}
      </p>

        {/* Click hint */}
        <div 
          style={{
            fontSize: '0.65rem',
            color: '#888',
            textAlign: 'center',
            marginTop: '0.4rem',
            opacity: 0.6
          }}
        >
          Click for details →
        </div>
      </div>
    </div>
  );
}

