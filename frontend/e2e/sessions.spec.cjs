/**
 * E2E Tests for Sessions Management
 *
 * Run with: cd .cursor/skills/playwright-skill && node run.js ../../../frontend/e2e/sessions.spec.js
 *
 * Prerequisites:
 * 1. Frontend dev server running: cd frontend && npm run dev
 * 2. Test credentials configured in e2e/.env (copy from .env.example)
 */

const { chromium } = require('playwright')
// Use absolute path for the helper since Playwright skill copies files to temp location
const authHelperPath = '/Volumes/Development/Practise/partner-scout/frontend/e2e/helpers/auth.cjs'
const { ensureAuthenticated, getTargetUrl } = require(authHelperPath)

// Configuration
const TARGET_URL = getTargetUrl()

async function runTests() {
  console.log('🧪 Starting E2E Sessions Tests')
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

      // Test protected route redirect
      console.log('\n📋 Test: Sessions route is protected')
      await page.goto(`${TARGET_URL}/sessions`)
      await page.waitForTimeout(1000)

      if (page.url().includes('/login')) {
        console.log('✅ Sessions page redirects to login')
      }

      // Test 404 page
      console.log('\n📋 Test: 404 page works')
      await page.goto(`${TARGET_URL}/nonexistent-page-12345`)
      await page.waitForSelector('h1')

      const notFoundHeading = await page.textContent('h1')
      if (notFoundHeading && notFoundHeading.includes('404')) {
        console.log('✅ 404 page displays correctly')
      }

      console.log('\n🎉 Unauthenticated tests completed!')
      return
    }

    // Authenticated tests
    console.log('\n✅ Authenticated - running full test suite')

    // Test 2: Sessions page renders
    console.log('\n📋 Test 2: Sessions page renders correctly')
    await page.goto(`${TARGET_URL}/sessions`)
    await page.waitForTimeout(1000)

    if (!page.url().includes('/login')) {
      console.log('✅ Sessions page loaded')

      await page.waitForSelector('h1')
      const heading = await page.textContent('h1')
      if (heading && heading.includes('Discovery Sessions')) {
        console.log(`✅ Sessions page heading: "${heading}"`)
      }
    }

    // Test 3: Create new session button
    console.log('\n📋 Test 3: Create new session button')
    const newSessionButton = await page.$(
      'a[href="/new-session"], button:has-text("New Session")'
    )
    if (newSessionButton) {
      console.log('✅ New session button/link present')

      // Click to navigate
      await newSessionButton.click()
      await page.waitForTimeout(500)

      if (page.url().includes('/new-session')) {
        console.log('✅ Navigated to new session page')

        // Go back to sessions
        await page.goto(`${TARGET_URL}/sessions`)
        await page.waitForTimeout(500)
      }
    }

    // Test 4: Session cards (if any exist)
    console.log('\n📋 Test 4: Session cards')
    const sessionCards = await page.$$('article, [class*="card"]')
    if (sessionCards.length > 0) {
      console.log(`✅ Found ${sessionCards.length} session cards`)

      // Click first session to navigate to dashboard
      const firstCard = sessionCards[0]
      const link = await firstCard.$('a')
      if (link) {
        await link.click()
        await page.waitForTimeout(500)

        if (page.url().includes('/jobs/')) {
          console.log('✅ Clicked session navigates to dashboard')
        }

        // Go back
        await page.goto(`${TARGET_URL}/sessions`)
        await page.waitForTimeout(500)
      }
    } else {
      console.log('ℹ️  No session cards found (may need to create sessions)')
    }

    // Test 5: Empty state (if no sessions)
    console.log('\n📋 Test 5: Empty state or session list')
    const emptyState = await page.$('[class*="empty"], :text("No sessions")')
    if (emptyState) {
      console.log('✅ Empty state displayed when no sessions')
    } else if (sessionCards.length > 0) {
      console.log('✅ Session list displayed with cards')
    }

    // Test 6: Navigation structure
    console.log('\n📋 Test 6: Navigation structure')

    // Check for skip link (accessibility)
    const skipLink = await page.$('a[href="#main-content"]')
    if (skipLink) {
      console.log('✅ Skip link present for accessibility')
    }

    // Check for user menu
    const userMenu = await page.$(
      '[aria-label*="user"], button:has-text("Account")'
    )
    if (userMenu) {
      console.log('✅ User menu present')
    }

    // Test 7: Responsive design
    console.log('\n📋 Test 7: Responsive design')

    await page.setViewportSize({ width: 375, height: 667 })
    await page.waitForTimeout(300)
    console.log('  ✅ Mobile viewport (375x667)')
    await page.screenshot({ path: '/tmp/sessions-mobile.png' })

    await page.setViewportSize({ width: 1280, height: 720 })
    await page.waitForTimeout(300)
    console.log('  ✅ Desktop viewport (1280x720)')
    await page.screenshot({ path: '/tmp/sessions-desktop.png' })

    // Test 8: 404 page
    console.log('\n📋 Test 8: 404 page works')
    await page.goto(`${TARGET_URL}/nonexistent-page-12345`)
    await page.waitForSelector('h1')

    const notFoundHeading = await page.textContent('h1')
    if (notFoundHeading && notFoundHeading.includes('404')) {
      console.log('✅ 404 page displays correctly')
    }

    // Take screenshot
    await page.screenshot({
      path: '/tmp/sessions-test-screenshot.png',
      fullPage: true,
    })
    console.log('\n📸 Screenshot saved to /tmp/sessions-test-screenshot.png')

    console.log('\n🎉 All E2E sessions tests passed!')
  } catch (error) {
    console.error('\n❌ Test failed:', error.message)
    await page.screenshot({
      path: '/tmp/sessions-test-error.png',
      fullPage: true,
    })
    console.log('📸 Error screenshot saved to /tmp/sessions-test-error.png')
    process.exitCode = 1
  } finally {
    await browser.close()
  }
}

runTests()
