import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  optimizeDeps: {
    include: [
      // Form libraries (DiscoveryConfigPage)
      'react-hook-form',
      '@hookform/resolvers/zod',
      'zod',
      // Radix UI components (DashboardPage, DiscoveryConfigPage)
      '@radix-ui/react-slider',
      '@radix-ui/react-tabs',
      '@radix-ui/react-select',
      '@radix-ui/react-dialog',
      // MUI icons used across lazy-loaded pages
      '@mui/icons-material/Add',
      '@mui/icons-material/ArrowBack',
      '@mui/icons-material/ArrowForward',
      '@mui/icons-material/RocketLaunch',
      '@mui/icons-material/Edit',
      '@mui/icons-material/Info',
      '@mui/icons-material/AccessTime',
      '@mui/icons-material/Dashboard',
      '@mui/icons-material/Delete',
      '@mui/icons-material/People',
      '@mui/icons-material/CheckCircle',
      '@mui/icons-material/CalendarToday',
      '@mui/icons-material/KeyboardArrowDown',
      '@mui/icons-material/Check',
      '@mui/icons-material/Star',
      '@mui/icons-material/Email',
      '@mui/icons-material/Score',
      '@mui/icons-material/StopCircle',
      '@mui/icons-material/Refresh',
      '@mui/icons-material/Mail',
      '@mui/icons-material/AutoAwesome',
      '@mui/icons-material/Send',
      '@mui/icons-material/SearchOff',
      '@mui/icons-material/OpenInNew',
      '@mui/icons-material/ContentCopy',
      '@mui/icons-material/Bookmark',
      '@mui/icons-material/BookmarkBorder',
      '@mui/icons-material/ThumbUp',
      '@mui/icons-material/Phone',
      '@mui/icons-material/LocationOn',
      '@mui/icons-material/Language',
      '@mui/icons-material/Visibility',
      '@mui/icons-material/TrendingUp',
      '@mui/icons-material/Search',
      '@mui/icons-material/PlayCircleOutline',
      '@mui/icons-material/ListAlt',
      // Date library
      'date-fns',
      // Supabase
      '@supabase/supabase-js',
      // React Query
      '@tanstack/react-query',
    ],
  },
})
