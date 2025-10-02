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

interface TopicModalProps {
  topic: Topic;
  onClose: () => void;
}

export function TopicModal({ topic, onClose }: TopicModalProps) {
  // Prevent body scroll when modal is open
  React.useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  // Close on escape key
  React.useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  const getColorClasses = (classification: string) => {
    if (classification.includes('CRITICAL')) {
      return { badge: '#dc2626', border: '#ef4444' };
    }
    if (classification.includes('EXPLOSIVE')) {
      return { badge: '#ea580c', border: '#f97316' };
    }
    if (classification.includes('TRENDING')) {
      return { badge: '#ca8a04', border: '#eab308' };
    }
    return { badge: '#16a34a', border: '#22c55e' };
  };

  const colors = getColorClasses(topic.classification);

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.85)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        padding: '2rem',
        backdropFilter: 'blur(8px)'
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: '#1c1e20',
          borderRadius: '16px',
          border: `2px solid ${colors.border}`,
          maxWidth: '600px',
          width: '100%',
          maxHeight: '80vh',
          overflow: 'auto',
          boxShadow: `0 20px 60px ${colors.border}40`,
          position: 'relative'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            background: 'rgba(255,255,255,0.1)',
            border: 'none',
            borderRadius: '8px',
            width: '36px',
            height: '36px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.5rem',
            color: '#fff',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(255,255,255,0.2)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(255,255,255,0.1)';
          }}
        >
          ✕
        </button>

        {/* Content */}
        <div style={{ padding: '2rem' }}>
          {/* Featured Image */}
          {topic.image_url && (
            <div 
              style={{
                width: '100%',
                height: '200px',
                overflow: 'hidden',
                borderRadius: '12px',
                marginBottom: '1.5rem',
                position: 'relative',
                background: 'rgba(255,255,255,0.05)'
              }}
            >
              <img 
                src={topic.image_url} 
                alt={topic.topic}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  filter: 'brightness(0.95) contrast(1.05)'
                }}
                onError={(e) => {
                  const parent = e.currentTarget.parentElement;
                  if (parent) parent.style.display = 'none';
                }}
              />
              {/* Subtle gradient overlay */}
              <div 
                style={{
                  position: 'absolute',
                  bottom: 0,
                  left: 0,
                  right: 0,
                  height: '50%',
                  background: 'linear-gradient(to top, rgba(28,30,32,0.8), transparent)'
                }}
              />
            </div>
          )}
          
          {/* Header */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
            <div
              style={{
                background: colors.badge,
                color: 'white',
                fontWeight: 700,
                fontSize: '1.2rem',
                padding: '8px 16px',
                borderRadius: '8px'
              }}
            >
              #{topic.rank}
            </div>
            <div style={{ fontSize: '2rem' }}>
              {topic.classification.split(' ')[0]}
            </div>
            <div
              style={{
                background: colors.badge,
                color: 'white',
                fontSize: '0.85rem',
                fontWeight: 700,
                padding: '6px 12px',
                borderRadius: '6px',
                marginLeft: 'auto'
              }}
            >
              {topic.explosiveness_score}/100
            </div>
          </div>

          {/* Title */}
          <h2
            style={{
              color: '#fff',
              fontSize: '1.5rem',
              fontWeight: 700,
              marginBottom: '1.5rem',
              lineHeight: '1.4'
            }}
          >
            {topic.topic}
          </h2>

          {/* Classification */}
          <div style={{ marginBottom: '1.5rem' }}>
            <div
              style={{
                display: 'inline-block',
                background: `${colors.badge}20`,
                color: colors.border,
                padding: '8px 16px',
                borderRadius: '8px',
                fontSize: '0.9rem',
                fontWeight: 600
              }}
            >
              {topic.classification}
            </div>
          </div>

          {/* Metrics */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '1rem',
              marginBottom: '1.5rem'
            }}
          >
            <div
              style={{
                background: 'rgba(255,255,255,0.05)',
                padding: '1rem',
                borderRadius: '8px',
                border: '1px solid rgba(255,255,255,0.1)'
              }}
            >
              <div style={{ fontSize: '0.75rem', color: '#999', marginBottom: '0.25rem' }}>
                Explosiveness Score
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: colors.border }}>
                {topic.explosiveness_score}
              </div>
            </div>
            <div
              style={{
                background: 'rgba(255,255,255,0.05)',
                padding: '1rem',
                borderRadius: '8px',
                border: '1px solid rgba(255,255,255,0.1)'
              }}
            >
              <div style={{ fontSize: '0.75rem', color: '#999', marginBottom: '0.25rem' }}>
                Article Count
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#d9f378' }}>
                {topic.frequency}
              </div>
            </div>
          </div>

          {/* Entities */}
          {topic.entities && (
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#fff', marginBottom: '0.75rem' }}>
                Key Entities
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {topic.entities.people && topic.entities.people.length > 0 && (
                  <div
                    style={{
                      background: 'rgba(255,255,255,0.05)',
                      padding: '0.75rem',
                      borderRadius: '8px',
                      border: '1px solid rgba(255,255,255,0.1)'
                    }}
                  >
                    <div style={{ fontSize: '0.75rem', color: '#999', marginBottom: '0.5rem' }}>
                      👤 People
                    </div>
                    <div style={{ color: '#e5e5e5', fontSize: '0.9rem' }}>
                      {topic.entities.people.join(', ')}
                    </div>
                  </div>
                )}
                {topic.entities.countries && topic.entities.countries.length > 0 && (
                  <div
                    style={{
                      background: 'rgba(255,255,255,0.05)',
                      padding: '0.75rem',
                      borderRadius: '8px',
                      border: '1px solid rgba(255,255,255,0.1)'
                    }}
                  >
                    <div style={{ fontSize: '0.75rem', color: '#999', marginBottom: '0.5rem' }}>
                      🌍 Countries
                    </div>
                    <div style={{ color: '#e5e5e5', fontSize: '0.9rem' }}>
                      {topic.entities.countries.join(', ')}
                    </div>
                  </div>
                )}
                {topic.entities.organizations && topic.entities.organizations.length > 0 && (
                  <div
                    style={{
                      background: 'rgba(255,255,255,0.05)',
                      padding: '0.75rem',
                      borderRadius: '8px',
                      border: '1px solid rgba(255,255,255,0.1)'
                    }}
                  >
                    <div style={{ fontSize: '0.75rem', color: '#999', marginBottom: '0.5rem' }}>
                      🏢 Organizations
                    </div>
                    <div style={{ color: '#e5e5e5', fontSize: '0.9rem' }}>
                      {topic.entities.organizations.join(', ')}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Reasoning */}
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#fff', marginBottom: '0.75rem' }}>
              Analysis
            </h3>
            <p
              style={{
                color: '#ccc',
                lineHeight: '1.6',
                fontSize: '0.9rem',
                background: 'rgba(255,255,255,0.05)',
                padding: '1rem',
                borderRadius: '8px',
                border: '1px solid rgba(255,255,255,0.1)'
              }}
            >
              {topic.reasoning}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

