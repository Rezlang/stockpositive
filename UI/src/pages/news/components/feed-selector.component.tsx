import React, { useState } from 'react';
import {
  Box,
  Checkbox,
  Button,
  Typography,
  Divider,
} from '@mui/joy';

type Option = {
  id: string;
  label: string;
};

type Category = {
  id: string;
  label: string;
  options: Option[];
};

const DATA: Category[] = [
  {
    id: 'stocks',
    label: 'Stocks',
    options: [
      { id: 'aapl', label: 'Apple' },
      { id: 'msft', label: 'Microsoft' },
    ],
  },
  {
    id: 'crypto',
    label: 'Crypto',
    options: [
      { id: 'btc', label: 'Bitcoin' },
      { id: 'eth', label: 'Ethereum' },
    ],
  },
];

const SelectableOptions: React.FC = () => {
  const [checked, setChecked] = useState<Record<string, boolean>>({});

  const toggleOption = (id: string) => {
    setChecked((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const toggleCategory = (category: Category) => {
    const allChecked = category.options.every(
      (opt) => checked[opt.id]
    );

    const updates: Record<string, boolean> = {};
    category.options.forEach((opt) => {
      updates[opt.id] = !allChecked;
    });

    setChecked((prev) => ({
      ...prev,
      ...updates,
    }));
  };

  const isCategoryChecked = (category: Category) =>
    category.options.every((opt) => checked[opt.id]);

  const isCategoryIndeterminate = (category: Category) => {
    const someChecked = category.options.some(
      (opt) => checked[opt.id]
    );
    return someChecked && !isCategoryChecked(category);
  };

  const handleSubmit = () => {
    const selectedOptions = Object.entries(checked)
      .filter(([, value]) => value)
      .map(([key]) => key);

    console.log('Selected options:', selectedOptions);
  };

  return (
    <Box sx={{ maxWidth: 400 }}>
      {DATA.map((category) => (
        <Box key={category.id}>
          {/* Category row */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              py: 1,
            }}
          >
            <Checkbox
              checked={isCategoryChecked(category)}
              indeterminate={isCategoryIndeterminate(category)}
              onChange={() => toggleCategory(category)}
            />
            <Typography level="title-sm">
              {category.label}
            </Typography>
          </Box>

          {/* Options */}
          {category.options.map((option) => (
            <Box
              key={option.id}
              sx={{
                display: 'flex',
                alignItems: 'center',
                pl: 4,
                py: 0.5,
              }}
            >
              <Checkbox
                checked={!!checked[option.id]}
                onChange={() => toggleOption(option.id)}
              />
              <Typography level="body-sm">
                {option.label}
              </Typography>
            </Box>
          ))}

          <Divider sx={{ my: 1 }} />
        </Box>
      ))}

      <Button onClick={handleSubmit} sx={{ mt: 2 }}>
        Submit
      </Button>
    </Box>
  );
};

export default SelectableOptions;
