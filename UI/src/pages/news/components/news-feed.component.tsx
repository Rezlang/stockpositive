import React from 'react';
import NewsCard from './news-card.component';
import { NEWSDATA } from '../constants/news-data.constant';

interface NewsFeedProps {
  cardsPerRow?: number;
}

export const NewsFeed: React.FC<NewsFeedProps> = ({ cardsPerRow = 1 }) => {
  const maxCardWidth = `calc((100% - 50px * 2) / 3)`;

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${cardsPerRow}, minmax(0, ${maxCardWidth}))`,
        gap: '50px',
        justifyContent: 'center',
        padding: '0 50px 0 20px',
      }}
    >
      {NEWSDATA.map((story) => (
        <NewsCard key={story.id} story={story} />
      ))}
    </div>
  );
};

export default NewsFeed;
