# StockPositive UI

This document describes the web and mobile applications for StockPositive.

## Structure

- **UI/web/** - React web application (Vite + React 19 + TypeScript + Material-UI)
- **UI/mobile/** - React Native mobile app (Expo + React Native + TypeScript)

## Getting Started

### Web Application

```bash
cd UI/web
npm install
npm run dev
```

Visit http://localhost:5173

### Mobile Application

```bash
cd UI/mobile
npm install
npm start
```

Scan QR code with Expo Go app or run on emulator.

- Press `i` for iOS simulator
- Press `a` for Android emulator
- Press `w` for web browser

## Technology Stack

**Web:**
- React 19
- TypeScript
- Vite
- React Router DOM
- Material-UI (MUI)
- Highcharts

**Mobile:**
- React Native
- TypeScript
- Expo
- React Navigation
- Ionicons

## Features

### Web App
- News feed with stock market news
- Interactive stock charts (candlestick/area)
- Feed customization options
- Stock selector
- News source filtering

### Mobile App
- Home screen with market overview
- Profile screen with portfolio information
- Bottom tab navigation
- TypeScript type safety

## Development

### Running Both Apps Simultaneously

Open two terminals:

Terminal 1 (Web):
```bash
cd UI/web
npm run dev
```

Terminal 2 (Mobile):
```bash
cd UI/mobile
npm start
```

## Building

### Web
```bash
cd UI/web
npm run build
```

### Mobile
```bash
cd UI/mobile
npm run build
```

## Project Structure

### Web (UI/web/src/)
```
src/
├── components/        # Reusable components
├── pages/            # Page components
│   ├── news/
│   ├── stock-chart/
│   └── feed-options/
├── routes.tsx        # Route definitions
└── App.tsx           # Root component
```

### Mobile (UI/mobile/src/)
```
src/
├── screens/          # Screen components
├── navigation/       # Navigation configuration
├── components/       # Reusable components
├── types/            # TypeScript types
├── services/         # API services
├── hooks/            # Custom hooks
└── utils/            # Utility functions
```

## Future Enhancements

- Backend API integration
- Shared types and utilities between web and mobile
- State management (Redux/Zustand)
- Authentication
- Real-time data updates
- Push notifications (mobile)
- Offline support (mobile)