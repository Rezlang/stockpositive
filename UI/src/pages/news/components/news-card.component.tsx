import React, { useState } from 'react';
import { Card, CardContent, Typography, AspectRatio, IconButton } from '@mui/joy';
import FavoriteIcon from '@mui/icons-material/Favorite';

interface NewsCardProps {
  story: any;
}

const NewsCard: React.FC<NewsCardProps> = ({ story }) => {
  const { title, thumbnail, provider, canonicalUrl } = story.content;
  const imageUrl = thumbnail?.originalUrl || thumbnail?.resolutions?.[0]?.url;

  const [liked, setLiked] = useState(false);

  const handleHeartClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setLiked(!liked);
  };

  return (
    <Card
      variant="outlined"
      sx={{
        width: '100%',
        transition: '0.3s',
        '&:hover': { boxShadow: 'md' },
        cursor: 'pointer',
        position: 'relative'
      }}
      onClick={() => window.open(canonicalUrl?.url || '#', '_blank')}
    >
      {imageUrl && (
        <div style={{ position: 'relative', width: '100%' }}>
            <AspectRatio ratio={16 / 9} sx={{ width: '100%', backgroundColor: 'red'}}>
                <img
                    src={imageUrl}
                    alt={title}
                    style={{
                        width: '100%',
                        height: 'auto',
                        borderRadius: 4,
                    }}
                />
            </AspectRatio>

          <IconButton
            size="sm"
            onClick={handleHeartClick}
            sx={{
                position: 'absolute',
                top: 8,
                right: 8,
                color: liked ? 'rgba(255,192,203,0.7)' : 'rgba(255,255,255,0.7)',
                bgcolor: 'rgba(0,0,0,0.4)',
                '&:hover': {
                    color: liked ? 'rgba(255,192,203,1)' : 'rgba(255,255,255,1)',
                    bgcolor: 'rgba(0,0,0,0.5)'
                }
                }}
          >
            <FavoriteIcon />
          </IconButton>
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

export default NewsCard;
