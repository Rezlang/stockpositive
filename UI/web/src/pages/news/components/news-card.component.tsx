import React from "react";
import { Card, CardContent, Typography, AspectRatio } from "@mui/joy";
import FavoriteIcon from "@mui/icons-material/Favorite";
import AddIcon from "@mui/icons-material/Add";
import OverlayIconButton from "./overlay-button.component";

interface NewsCardProps {
  story: any;
}

const NewsCard: React.FC<NewsCardProps> = ({ story }) => {
  const { title, thumbnail, provider, canonicalUrl } = story.content;
  const imageUrl = thumbnail?.originalUrl || thumbnail?.resolutions?.[0]?.url;

  return (
    <Card
      variant="outlined"
      sx={{
        width: "100%",
        transition: "0.3s",
        "&:hover": { boxShadow: "md" },
        cursor: "pointer",
        position: "relative",
      }}
      onClick={() => window.open(canonicalUrl?.url || "#", "_blank")}
    >
      {imageUrl && (
        <div style={{ position: "relative", width: "100%" }}>
          <AspectRatio ratio={16 / 9} sx={{ width: "100%" }}>
            <img
              src={imageUrl}
              alt={title}
              style={{
                width: "100%",
                height: "auto",
                borderRadius: 4,
              }}
            />
          </AspectRatio>

          <OverlayIconButton
            icon={<AddIcon />}
            hoverColor="rgba(255,255,255,1)"
            activeHoverColor="rgba(144,202,249,0.8)"
            activeColor="rgba(144,202,249,1)"
            left={8}
            onToggle={(active) => console.log("Add toggled:", active)}
          />

          <OverlayIconButton
            icon={<FavoriteIcon />}
            hoverColor="rgba(255,255,255,1)"
            activeColor="rgba(255,192,203,0.8)"
            activeHoverColor="rgba(255,192,203,1)"
            right={8}
            onToggle={(active) => console.log("Liked:", active)}
          />

          {thumbnail?.caption && (
            <Typography
              level="body-xs"
              sx={{
                position: "absolute",
                bottom: 0,
                left: 0,
                right: 0,
                bgcolor: "rgba(0,0,0,0.5)",
                color: "#fff",
                p: 0.5,
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
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
