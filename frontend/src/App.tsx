import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-4">
      <div className="card max-w-lg w-full text-center">
        <div className="mb-6">
          <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            PartnerScout AI
          </h1>
          <p className="text-gray-500">
            AI-powered Instagram partner discovery platform
          </p>
        </div>

        <div className="space-y-3 mb-6">
          <div className="flex items-center gap-3 p-3 bg-success-50 rounded-xl">
            <div className="w-2 h-2 bg-success-500 rounded-full"></div>
            <span className="text-sm text-success-600 font-medium">
              Frontend Running
            </span>
          </div>
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
            <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
            <span className="text-sm text-gray-500">
              Backend: http://localhost:8000
            </span>
          </div>
        </div>

        <div className="flex gap-3 justify-center">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary"
          >
            API Docs
          </a>
          <button className="btn-primary">
            Get Started
          </button>
        </div>

        <p className="text-xs text-gray-400 mt-6">
          Version 1.0.0 • Development Mode
        </p>
      </div>
    </div>
  )
}

export default App
