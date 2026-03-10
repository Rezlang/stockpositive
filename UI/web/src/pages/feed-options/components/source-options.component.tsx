import React, { useState, useEffect } from "react";
import { Box, Checkbox, Button, Typography, Divider } from "@mui/joy";
import KeyboardArrowRight from "@mui/icons-material/KeyboardArrowRight";
import KeyboardArrowDown from "@mui/icons-material/KeyboardArrowDown";
import type { TreeNode } from "../constants/source-options.constant";
import { SOURCEOPTIONS } from "../constants/source-options.constant";

/* ---------- Helpers ---------- */

const collectLeafIds = (node: TreeNode): string[] => {
  if (!node.children || node.children.length === 0) {
    return [node.id];
  }
  return node.children.flatMap(collectLeafIds);
};

/* ---------- Component ---------- */

const SourceOptions: React.FC = () => {
  const [checked, setChecked] = useState<Record<string, boolean>>({});
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const init: Record<string, boolean> = {};
    const walk = (nodes: TreeNode[], depth = 0) => {
      nodes.forEach((node) => {
        if (node.children) {
          init[node.id] = depth < 2;
          walk(node.children, depth + 1);
        }
      });
    };
    walk(SOURCEOPTIONS);
    setExpanded(init);
  }, []);

  const isChecked = (node: TreeNode) =>
    collectLeafIds(node).every((id) => checked[id]);

  const isIndeterminate = (node: TreeNode) => {
    const leafIds = collectLeafIds(node);
    const someChecked = leafIds.some((id) => checked[id]);
    return someChecked && !isChecked(node);
  };

  const toggleNode = (node: TreeNode) => {
    const leafIds = collectLeafIds(node);
    const shouldCheck = !leafIds.every((id) => checked[id]);
    const updates: Record<string, boolean> = {};
    leafIds.forEach((id) => {
      updates[id] = shouldCheck;
    });
    setChecked((prev) => ({ ...prev, ...updates }));
  };

  const toggleExpand = (id: string) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const renderTags = (tags?: TreeNode["tags"]) => {
    if (!tags || tags.length === 0) return null;
    return (
      <Box sx={{ display: "flex", gap: 0.5, ml: 1 }}>
        {tags.map((tag) => (
          <Box
            key={tag}
            sx={{
              px: 1,
              py: "2px",
              borderRadius: "999px",
              fontSize: "0.7rem",
              fontWeight: "bold",
              textTransform: "uppercase",
              color: tag === "promoted" ? "white" : "black",
              backgroundColor: tag === "promoted" ? "green" : "gold",
            }}
          >
            {tag}
          </Box>
        ))}
      </Box>
    );
  };

  const renderNode = (node: TreeNode, depth = 0) => {
    const hasChildren = !!node.children?.length;
    const isOpen = expanded[node.id];

    return (
      <Box key={node.id}>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            pl: depth * 3,
            py: 0.5,
            minHeight: 30,
          }}
        >
          <Checkbox
            checked={isChecked(node)}
            indeterminate={isIndeterminate(node)}
            onChange={() => toggleNode(node)}
          />

          <Typography
            component="div"
            level={depth === 0 ? "title-sm" : "body-sm"}
            sx={{
              flexGrow: 1,
              paddingLeft: 2,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
            }}
            onClick={() => {
              if (hasChildren) {
                toggleExpand(node.id);
              } else {
                toggleNode(node);
              }
            }}
          >
            {node.label}
            {renderTags(node.tags)}

            {hasChildren && (
              <Box
                component="span"
                sx={{ ml: 1, display: "flex", alignItems: "center" }}
              >
                {isOpen ? <KeyboardArrowDown /> : <KeyboardArrowRight />}
              </Box>
            )}
          </Typography>
        </Box>
        {hasChildren && isOpen && (
          <Box>
            {node.children!.map((child) => renderNode(child, depth + 1))}
          </Box>
        )}

        {depth === 0 && <Divider sx={{ my: 1 }} />}
      </Box>
    );
  };

  const handleSubmit = () => {
    const selected = Object.entries(checked)
      .filter(([, value]) => value)
      .map(([key]) => key);

    console.log("Selected leaf nodes:", selected);
  };

  return (
    <Box sx={{ maxWidth: 500 }}>
      <Typography level="body-sm" sx={{ mb: 2, color: "neutral.500" }}>
        Leave all sources unselected to receive news from all sources
      </Typography>
      {SOURCEOPTIONS.map((node) => renderNode(node))}
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          mt: 2,
          paddingBottom: 10,
        }}
      >
        <Button onClick={handleSubmit}>Submit</Button>
      </Box>
    </Box>
  );
};

export default SourceOptions;
