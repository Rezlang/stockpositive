import React from 'react';
import { Card, CardContent, Typography, AspectRatio } from '@mui/joy';
import { NEWSDATA } from '../constants/news-data.constant';

const NewsCard: React.FC<{ story: any }> = ({ story }) => {
  const { title, thumbnail, provider, canonicalUrl } = story.content;
  const imageUrl = thumbnail?.originalUrl || thumbnail?.resolutions?.[0]?.url;

  return (
    <Card
      variant="outlined"
      sx={{
        width: '100%',
        transition: '0.3s',
        '&:hover': { boxShadow: 'md' },
        cursor: 'pointer',
      }}
      onClick={() => window.open(canonicalUrl?.url || '#', '_blank')}
    >
      {imageUrl && (
        <div style={{ position: 'relative', width: '100%' }}>
          <AspectRatio ratio={16 / 9} sx={{ width: '100%' }}>
            <img
              src={imageUrl}
              alt={title}
              style={{ objectFit: 'cover', width: '100%', height: '100%' }}
            />
          </AspectRatio>
          {thumbnail?.caption && (
            <Typography
              level="body-xs"
              sx={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                bgcolor: 'rgba(0,0,0,0.5)',
                color: '#fff',
                p: 0.5,
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {thumbnail.caption}
            </Typography>
          )}
        </div>
      )}
      <CardContent>
        <Typography level="title-md" sx={{ mb: 0.5 }}>
          {title}
        </Typography>
        <Typography level="body-sm" textColor="text.tertiary">
          {provider?.displayName}
        </Typography>
      </CardContent>
    </Card>
  );
};

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
        padding: '0 50px 0 20px'
      }}
    >
      {NEWSDATA.map((story) => (
        <NewsCard key={story.id} story={story} />
      ))}
    </div>
  );
};
