import type { RouteObject } from 'react-router-dom'
import Candles from './pages/news/news.page.tsx'
const routes: RouteObject[] = [
  {
    path: '/',
    element: <Candles />,
  },
]

export default routes
