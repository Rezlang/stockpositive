import NewsFeed from "./components/news-feed.component"

function NewsPage() {
  return (
    <div style={{
      marginTop: '40px',
      textAlign: 'center',
    }}>
        <h2>Related News</h2>
        <NewsFeed cardsPerRow={2} />
      </div>
  )
}

export default NewsPage
