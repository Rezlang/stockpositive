import StockChart from './components/stock-chart.component'
import NewsFeed from './components/news-feed.component'
import SelectableOptions from './components/feed-selector.component'

function Candles() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Candles Page</h1>
      <StockChart />

      <div style={{ marginTop: '40px' }}>
        <h2>Related News</h2>
        <NewsFeed />
      </div>

      <SelectableOptions />
    </div>
  )
}

export default Candles
