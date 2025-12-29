import type { RouteObject } from "react-router-dom";
import { Navigate } from "react-router-dom";
import NewsPage from "./pages/news/news.page.tsx";
import StockChartPage from "./pages/stock-chart/stock-chart.page.tsx";
import FeedOptionsPage from "./pages/feed-options/feed-options.page.tsx";
const routes: RouteObject[] = [
  {
    path: "/",
    element: <Navigate to="/news" replace />,
  },
  {
    path: "/news",
    element: <NewsPage />,
  },
  {
    path: "/stock-chart",
    element: <StockChartPage />,
  },
  {
    path: "/feed-options",
    element: <FeedOptionsPage />,
  },
];

export default routes;
