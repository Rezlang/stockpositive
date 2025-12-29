import React, { useState } from "react";
import { IconButton } from "@mui/joy";

interface OverlayIconButtonProps {
  icon: React.ReactNode;
  activeIcon?: React.ReactNode;
  hoverColor: string;
  activeColor: string;
  activeHoverColor?: string;
  onToggle?: (active: boolean) => void;
  top?: number;
  right?: number;
  left?: number;
}

const OverlayIconButton: React.FC<OverlayIconButtonProps> = ({
  icon,
  activeIcon,
  hoverColor,
  activeColor,
  activeHoverColor,
  onToggle,
  top = 8,
  right,
  left,
}) => {
  const [active, setActive] = useState(false);

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setActive((prev) => {
      const next = !prev;
      onToggle?.(next);
      return next;
    });
  };

  return (
    <IconButton
      size="sm"
      onClick={handleClick}
      sx={{
        position: "absolute",
        top,
        right,
        left,
        color: active ? activeColor : "rgba(255,255,255,0.8)",
        bgcolor: "rgba(0,0,0,0.45)",
        transition:
          "color 0.25s ease, background-color 0.25s ease, transform 0.2s ease",
        "&:hover": {
          color: active ? activeHoverColor || hoverColor : hoverColor,
          bgcolor: "rgba(0,0,0,0.55)",
          transform: "scale(1.05)",
        },
        "&:active": {
          transform: "scale(0.95)",
        },
      }}
    >
      {active && activeIcon ? activeIcon : icon}
    </IconButton>
  );
};

export default OverlayIconButton;
