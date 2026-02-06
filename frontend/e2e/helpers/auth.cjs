/**
 * E2E Authentication Helper
 *
 * Provides login functionality for Playwright tests to access protected routes.
 * Uses session caching to speed up subsequent test runs.
 *
 * Usage:
 *   const { login, ensureAuthenticated } = require('./helpers/auth')
 *
 *   // In your test:
 *   await ensureAuthenticated(page, context)
 *   // Now navigate to protected routes
 */

const fs = require('fs')

// Session file location
const SESSION_FILE = '/tmp/partner-scout-e2e-session.json'

// Load .env file FIRST before anything else
function loadEnvFile() {
  // Use absolute path since this file may be required from a copied temp file
  const envPath = '/Volumes/Development/Practise/partner-scout/frontend/e2e/.env'
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf8')
    const lines = envContent.split('\n')

    for (const line of lines) {
      const trimmed = line.trim()
      if (trimmed && !trimmed.startsWith('#')) {
        const [key, ...valueParts] = trimmed.split('=')
        const value = valueParts.join('=').trim()
        if (key && value) {
          // Always set the env var (override if already set)
          process.env[key] = value.replace(/^["']|["']$/g, '')
        }
      }
    }
    console.log('📁 Loaded environment from e2e/.env')
  }
}

// Auto-load .env on require - MUST be called first!
loadEnvFile()

/**
 * Get credentials from environment (called at runtime, after .env loaded)
 */
function getCredentials() {
  return {
    email: process.env.E2E_TEST_EMAIL || process.env.TEST_EMAIL,
    password: process.env.E2E_TEST_PASSWORD || process.env.TEST_PASSWORD,
  }
}

/**
 * Get the target URL for tests
 * @returns {string}
 */
function getTargetUrl() {
  return process.env.TEST_URL || 'http://localhost:5173'
}

/**
 * Check if credentials are configured
 * @returns {boolean}
 */
function hasCredentials() {
  const { email, password } = getCredentials()
  return !!(email && password)
}

/**
 * Log in via the UI
 * @param {import('playwright').Page} page - Playwright page instance
 * @param {string} [email] - Optional email override
 * @param {string} [password] - Optional password override
 * @returns {Promise<boolean>} - true if login successful
 */
async function login(page, email, password) {
  const creds = getCredentials()
  const loginEmail = email || creds.email
  const loginPassword = password || creds.password

  if (!loginEmail || !loginPassword) {
    console.log('⚠️  No test credentials configured')
    console.log('   Set E2E_TEST_EMAIL and E2E_TEST_PASSWORD environment variables')
    console.log('   Or create frontend/e2e/.env file with these values')
    return false
  }

  console.log(`🔐 Logging in as ${loginEmail}...`)

  const targetUrl = getTargetUrl()

  // Navigate to login page
  await page.goto(`${targetUrl}/login`)
  await page.waitForSelector('input[type="email"]', { timeout: 10000 })

  // Fill in credentials
  await page.fill('input[type="email"]', loginEmail)
  await page.fill('input[type="password"]', loginPassword)

  // Submit form
  await page.click('button[type="submit"]')

  // Wait for redirect to authenticated area (sessions page)
  try {
    await page.waitForURL('**/sessions**', { timeout: 15000 })
    console.log('✅ Login successful - redirected to sessions')
    return true
  } catch (error) {
    // Check if we're still on login page with an error
    const currentUrl = page.url()
    if (currentUrl.includes('/login')) {
      // Look for error message
      const errorMessage = await page.$('[role="alert"]')
      if (errorMessage) {
        const text = await errorMessage.textContent()
        console.log(`❌ Login failed: ${text}`)
      } else {
        console.log('❌ Login failed: Check credentials')
      }
      return false
    }

    // Maybe redirected elsewhere (dashboard, etc.)
    if (!currentUrl.includes('/login')) {
      console.log(`✅ Login successful - on ${currentUrl}`)
      return true
    }

    throw error
  }
}

/**
 * Save the current session state to a file
 * @param {import('playwright').BrowserContext} context - Browser context
 * @param {string} [filePath] - Optional custom path
 */
async function saveSession(context, filePath = SESSION_FILE) {
  await context.storageState({ path: filePath })
  console.log(`💾 Session saved to ${filePath}`)
}

/**
 * Check if a saved session exists and is valid
 * @param {string} [filePath] - Optional custom path
 * @returns {boolean}
 */
function hasStoredSession(filePath = SESSION_FILE) {
  if (!fs.existsSync(filePath)) {
    return false
  }

  // Check if file is recent (less than 1 hour old)
  const stats = fs.statSync(filePath)
  const ageMs = Date.now() - stats.mtimeMs
  const oneHour = 60 * 60 * 1000

  if (ageMs > oneHour) {
    console.log('🔄 Stored session expired, will re-authenticate')
    fs.unlinkSync(filePath)
    return false
  }

  return true
}

/**
 * Create a browser context with stored session
 * @param {import('playwright').Browser} browser - Playwright browser
 * @param {object} [options] - Context options
 * @returns {Promise<import('playwright').BrowserContext>}
 */
async function createAuthenticatedContext(browser, options = {}) {
  if (hasStoredSession()) {
    console.log('♻️  Reusing stored session')
    return browser.newContext({
      storageState: SESSION_FILE,
      ...options,
    })
  }
  return browser.newContext(options)
}

/**
 * Ensure the page is authenticated
 * Logs in if needed, and saves session for future use
 *
 * @param {import('playwright').Page} page - Playwright page
 * @param {import('playwright').BrowserContext} context - Browser context
 * @returns {Promise<boolean>} - true if authenticated
 */
async function ensureAuthenticated(page, context) {
  const targetUrl = getTargetUrl()

  // First check if we already have a valid session
  if (hasStoredSession()) {
    // Verify by navigating to a protected route
    await page.goto(`${targetUrl}/sessions`)
    await page.waitForTimeout(1000)

    const url = page.url()
    if (!url.includes('/login')) {
      console.log('✅ Already authenticated (from stored session)')
      return true
    }

    // Session expired or invalid, delete it
    console.log('⚠️  Stored session invalid, re-authenticating...')
    if (fs.existsSync(SESSION_FILE)) {
      fs.unlinkSync(SESSION_FILE)
    }
  }

  // No valid session, need to login
  if (!hasCredentials()) {
    console.log('⚠️  No credentials configured - cannot authenticate')
    console.log('   Tests will run on login page only')
    return false
  }

  const success = await login(page)
  if (success) {
    // Save session for future tests
    await saveSession(context)
  }

  return success
}

/**
 * Clear stored session (useful for testing logout)
 */
function clearSession(filePath = SESSION_FILE) {
  if (fs.existsSync(filePath)) {
    fs.unlinkSync(filePath)
    console.log('🗑️  Stored session cleared')
  }
}

module.exports = {
  login,
  saveSession,
  hasStoredSession,
  createAuthenticatedContext,
  ensureAuthenticated,
  clearSession,
  hasCredentials,
  getTargetUrl,
  getCredentials,
  SESSION_FILE,
}
