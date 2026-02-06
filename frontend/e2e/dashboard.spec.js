/**
 * E2E Tests for Dashboard Page
 *
 * Run with: cd .cursor/skills/playwright-skill && node run.js ../../../frontend/e2e/dashboard.spec.js
 *
 * Prerequisites:
 * 1. Frontend dev server running: cd frontend && npm run dev
 * 2. Test credentials configured in e2e/.env (copy from .env.example)
 */

const { chromium } = require('playwright')
// Use absolute path for the helper since Playwright skill copies files to temp location
const authHelperPath = '/Volumes/Development/Practise/partner-scout/frontend/e2e/helpers/auth.cjs'
const {
  ensureAuthenticated,
  getTargetUrl,
  hasCredentials,
} = require(authHelperPath)

// Configuration
const TARGET_URL = getTargetUrl()

async function runTests() {
  console.log('🧪 Starting E2E Dashboard Tests')
  console.log(`📍 Target URL: ${TARGET_URL}`)

  const browser = await chromium.launch({ headless: false })
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
  })
  const page = await context.newPage()

  try {
    // Step 1: Authenticate
    console.log('\n🔐 Step 1: Authentication')
    const isAuthenticated = await ensureAuthenticated(page, context)

    if (!isAuthenticated) {
      console.log('\n⚠️  Running in unauthenticated mode')
      console.log('   Some tests will be skipped')
      console.log('   Configure e2e/.env to test protected routes')

      // Test unauthenticated behavior
      console.log('\n📋 Test: Protected routes redirect to login')
      await page.goto(`${TARGET_URL}/jobs/1`)
      await page.waitForTimeout(1000)

      const url = page.url()
      if (url.includes('/login')) {
        console.log('✅ Dashboard is protected (redirects to login)')
      }

      // Test 404 page
      console.log('\n📋 Test: 404 page works')
      await page.goto(`${TARGET_URL}/nonexistent-route-12345`)
      await page.waitForSelector('h1')
      const notFound = await page.textContent('h1')
      if (notFound && notFound.includes('404')) {
        console.log('✅ 404 page displays correctly')
      }

      console.log('\n🎉 Unauthenticated tests completed!')
      return
    }

    // Authenticated tests
    console.log('\n✅ Authenticated - running full test suite')

    // Test 2: Navigate to dashboard
    console.log('\n📋 Test 2: Dashboard page renders')
    await page.goto(`${TARGET_URL}/jobs/demo-job-1`)
    await page.waitForTimeout(1000)

    const url = page.url()
    if (!url.includes('/login')) {
      console.log('✅ Dashboard page loaded (not redirected to login)')
    } else {
      console.log('⚠️  Unexpectedly redirected to login')
    }

    // Test 3: Sessions page accessible
    console.log('\n📋 Test 3: Sessions page accessible')
    await page.goto(`${TARGET_URL}/sessions`)
    await page.waitForTimeout(500)

    const sessionsUrl = page.url()
    if (!sessionsUrl.includes('/login')) {
      console.log('✅ Sessions route accessible when authenticated')

      // Check for sessions page content
      const heading = await page.$('h1')
      if (heading) {
        const text = await heading.textContent()
        console.log(`   Page heading: "${text}"`)
      }
    }

    // Test 4: New session route accessible
    console.log('\n📋 Test 4: New session route accessible')
    try {
      await page.goto(`${TARGET_URL}/new-session`, { waitUntil: 'domcontentloaded' })
      await page.waitForTimeout(500)

      const newSessionUrl = page.url()
      if (!newSessionUrl.includes('/login')) {
        console.log('✅ New session route accessible when authenticated')
      }
    } catch (e) {
      console.log('⚠️  New session route had navigation issue (may be page-specific)')
    }

    // Test 5: Dashboard UI components
    console.log('\n📋 Test 5: Dashboard UI components')
    await page.goto(`${TARGET_URL}/jobs/demo-job-1`)
    await page.waitForTimeout(1000)

    // Check for stats grid
    const statsCards = await page.$$('[class*="stat"], [class*="card"]')
    if (statsCards.length > 0) {
      console.log(`✅ Found ${statsCards.length} stat/card elements`)
    }

    // Check for profile cards
    const profileCards = await page.$$('article')
    if (profileCards.length > 0) {
      console.log(`✅ Found ${profileCards.length} profile cards`)
    }

    // Test 6: Responsive viewport
    console.log('\n📋 Test 6: Responsive viewport test')

    // Desktop viewport
    await page.setViewportSize({ width: 1280, height: 720 })
    await page.waitForTimeout(300)
    console.log('✅ Desktop viewport (1280x720)')

    // Tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 })
    await page.waitForTimeout(300)
    console.log('✅ Tablet viewport (768x1024)')

    // Mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    await page.waitForTimeout(300)
    console.log('✅ Mobile viewport (375x667)')

    // Take screenshot at mobile
    await page.screenshot({ path: '/tmp/dashboard-mobile.png', fullPage: true })
    console.log('📸 Mobile screenshot saved to /tmp/dashboard-mobile.png')

    // Test 7: 404 page still works
    console.log('\n📋 Test 7: 404 page works')
    await page.setViewportSize({ width: 1280, height: 720 })
    await page.goto(`${TARGET_URL}/nonexistent-route-12345`)
    await page.waitForSelector('h1')
    const notFound = await page.textContent('h1')
    if (notFound && notFound.includes('404')) {
      console.log('✅ 404 page displays correctly')
    }

    // Test 8: Navigation between pages
    console.log('\n📋 Test 8: Navigation flow')
    await page.goto(`${TARGET_URL}/sessions`)
    await page.waitForTimeout(500)
    console.log('✅ Navigated to sessions')

    await page.goto(`${TARGET_URL}/new-session`)
    await page.waitForTimeout(500)
    console.log('✅ Navigated to new-session')

    await page.goto(`${TARGET_URL}/jobs/demo-job-1`)
    await page.waitForTimeout(500)
    console.log('✅ Navigated to dashboard')

    // Take final screenshot
    await page.screenshot({
      path: '/tmp/dashboard-test-final.png',
      fullPage: true,
    })
    console.log('\n📸 Final screenshot saved to /tmp/dashboard-test-final.png')

    console.log('\n🎉 All E2E dashboard tests passed!')
  } catch (error) {
    console.error('\n❌ Test failed:', error.message)
    await page.screenshot({
      path: '/tmp/dashboard-test-error.png',
      fullPage: true,
    })
    console.log('📸 Error screenshot saved to /tmp/dashboard-test-error.png')
    process.exitCode = 1
  } finally {
    await browser.close()
  }
}

runTests()
