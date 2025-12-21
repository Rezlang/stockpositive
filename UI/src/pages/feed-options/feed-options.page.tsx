import SourceOptions from './components/source-options.component'
import StockSelector from './components/stock-selector'

function FeedOptionsPage() {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      flexDirection: 'column',
      paddingTop: '40px', 
    }}>
      <StockSelector />
      <SourceOptions />
    </div>
  )
}

export default FeedOptionsPage