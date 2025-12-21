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
        maxWidth: 320,
        m: 2,
        flexShrink: 0,
        transition: '0.3s',
        '&:hover': { boxShadow: 'md' },
        cursor: 'pointer',
      }}
      onClick={() => window.open(canonicalUrl?.url || '#', '_blank')}
    >
      {imageUrl && (
        <div style={{ position: 'relative', width: '100%' }}>
        <AspectRatio ratio={16 / 9}>
          <img src={imageUrl} alt={title} style={{ objectFit: 'cover', width: '100%', height: '100%' }} />
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

const NewsFeed: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      {NEWSDATA.map((story) => (
        <div key={story.id} style={{ width: '100%', maxWidth: 600, margin: '10px 0' }}>
          <NewsCard story={story} />
        </div>
      ))}
    </div>
  );
};

export default NewsFeed;
