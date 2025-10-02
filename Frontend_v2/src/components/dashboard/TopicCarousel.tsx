import React, { useState, useEffect, useRef } from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination, Autoplay } from 'swiper/modules';
import type { Swiper as SwiperType } from 'swiper';
import { TopicCard } from './TopicCard';
import { TopicModal } from './TopicModal';

// Import Swiper styles
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import './TopicCarousel.css';

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

interface TopicCarouselProps {
  topics: Topic[];
  loading?: boolean;
}

export function TopicCarousel({ topics, loading }: TopicCarouselProps) {
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
  const [isPaused, setIsPaused] = useState(false);
  const swiperRef = useRef<SwiperType | null>(null);

  // Auto-refresh simulation (in real app, this would poll the API)
  useEffect(() => {
    if (topics.length > 0 && swiperRef.current) {
      // Reset to first slide when topics update
      swiperRef.current.slideTo(0);
    }
  }, [topics]);

  if (loading) {
    return (
      <div className="carousel-container">
        <div className="carousel-skeleton">
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton-card">
              <div className="skeleton-shimmer"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (topics.length === 0) {
    return (
      <div className="carousel-empty">
        <div className="empty-icon">🔍</div>
        <h3>No explosive topics yet</h3>
        <p>Enter keywords and click Refresh to discover trending topics</p>
      </div>
    );
  }

  return (
    <>
      <div 
        className="carousel-container"
        onMouseEnter={() => setIsPaused(true)}
        onMouseLeave={() => setIsPaused(false)}
      >
        {/* Carousel Header */}
        <div className="carousel-header">
          <div className="carousel-title">
            <span className="live-indicator">🔴</span>
            <h3>Live Explosive Topics</h3>
            <span className="topic-count">{topics.length} topics</span>
          </div>
          {isPaused && (
            <div className="pause-indicator">
              ⏸️ Paused
            </div>
          )}
        </div>

        {/* Swiper Carousel */}
        <Swiper
          modules={[Navigation, Pagination, Autoplay]}
          spaceBetween={20}
          slidesPerView={1}
          navigation
          pagination={{ 
            clickable: true,
            dynamicBullets: true 
          }}
          autoplay={{
            delay: 4000,
            disableOnInteraction: false,
            pauseOnMouseEnter: true
          }}
          loop={topics.length > 3}
          speed={500}
          breakpoints={{
            640: {
              slidesPerView: 1,
              spaceBetween: 15
            },
            768: {
              slidesPerView: 2,
              spaceBetween: 15
            },
            1024: {
              slidesPerView: 3,
              spaceBetween: 20
            },
            1280: {
              slidesPerView: 4,
              spaceBetween: 20
            }
          }}
          onSwiper={(swiper) => {
            swiperRef.current = swiper;
          }}
          className="topics-swiper"
        >
          {topics.map((topic) => (
            <SwiperSlide key={topic.rank}>
              <TopicCard 
                topic={topic} 
                onClick={() => setSelectedTopic(topic)} 
              />
            </SwiperSlide>
          ))}
        </Swiper>

        {/* Progress Indicator */}
        <div className="carousel-footer">
          <div className="auto-scroll-indicator">
            <span className="indicator-icon">⟳</span>
            <span>Auto-scrolling every 4s • Hover to pause</span>
          </div>
        </div>
      </div>

      {/* Modal */}
      {selectedTopic && (
        <TopicModal 
          topic={selectedTopic} 
          onClose={() => setSelectedTopic(null)} 
        />
      )}
    </>
  );
}

