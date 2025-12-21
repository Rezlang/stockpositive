export type TreeNode = {
  id: string; label: string;
  children?: TreeNode[];
  tags?: ('promoted'|'recommended')[];
};

/* ---------- Sample Data with Tags ---------- */

export const SOURCEOPTIONS: TreeNode[] = [
  {
    id: 'legacy-news',
    label: 'Legacy Financial News',
    children: [
      {id: 'wsj', label: 'Wall Street Journal', tags: ['recommended']},
      {id: 'ft', label: 'Financial Times'},
      {id: 'bloomberg', label: 'Bloomberg', tags: ['promoted']},
    ],
  },
  {
    id: 'modern-news',
    label: 'Modern Financial News',
    children: [
      {id: 'seeking-alpha', label: 'Seeking Alpha', tags: ['promoted']},
      {id: 'motley-fool', label: 'The Motley Fool'},
    ],
  },
  {
    id: 'social-media',
    label: 'Social Media',
    children: [
      {
        id: 'reddit',
        label: 'Reddit',
        children: [
          {
            id: 'reddit-users',
            label: 'Users',
            children: [
              {id: 'u-wallstreetbets', label: 'u/wallstreetbets'},
              {
                id: 'u-financeguru',
                label: 'u/financeguru',
                tags: ['recommended']
              },
            ],
          },
          {
            id: 'reddit-subreddits',
            label: 'Subreddits',
            children: [
              {id: 'r-investing', label: 'r/investing'},
              {id: 'r-stocks', label: 'r/stocks', tags: ['promoted']},
              {id: 'r-wallstreetbets', label: 'r/wallstreetbets'},
            ],
          },
        ],
      },
    ],
  },
];