import { NavLink } from 'react-router-dom'

type HeaderItem = {
  label: string
  to: string
}

const headerItems: HeaderItem[] = [
  { label: 'News', to: '/news' },
  { label: 'Stock Chart', to: '/stock-chart' },
  { label: 'Feed Options', to: '/feed-options' },
]

function AppHeader() {
  return (
    <header style={styles.header}>
      <nav style={styles.nav}>
        {headerItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            style={({ isActive }) => ({
              ...styles.link,
              fontWeight: isActive ? 'bold' : 'normal',
              textDecoration: isActive ? 'underline' : 'none',
            })}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </header>
  )
}

const styles = {
  header: {
    padding: '12px 16px',
    borderBottom: '1px solid #ddd',
  },
  nav: {
    display: 'flex',
    gap: '16px',
  },
  link: {
    color: '#000',
  },
}

export default AppHeader
