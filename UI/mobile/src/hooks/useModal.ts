import { useState, useCallback } from 'react';

interface UseModalResult {
  isVisible: boolean;
  show: () => void;
  hide: () => void;
  toggle: () => void;
}

export function useModal(initial = false): UseModalResult {
  const [isVisible, setIsVisible] = useState(initial);

  const show = useCallback(() => setIsVisible(true), []);
  const hide = useCallback(() => setIsVisible(false), []);
  const toggle = useCallback(() => setIsVisible((prev) => !prev), []);

  return { isVisible, show, hide, toggle };
}
