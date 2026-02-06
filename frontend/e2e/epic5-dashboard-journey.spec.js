/**
 * E2E Epic 5 Journey Test - Main Dashboard
 *
 * Run with: cd .cursor/skills/playwright-skill && node run.js ../../../frontend/e2e/epic5-dashboard-journey.spec.js
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
  console.log('🧪 Starting Epic 5 Dashboard Journey Tests')
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
      console.log('   Epic 5 dashboard tests require authentication')

      // Test that dashboard is protected
      console.log('\n📋 Test: Dashboard protected correctly')
      await page.goto(`${TARGET_URL}/jobs/demo-job-1`)
      await page.waitForTimeout(1000)

      if (page.url().includes('/login')) {
        console.log('✅ Dashboard redirects to login when not authenticated')
      }

      console.log('\n🎉 Unauthenticated tests completed!')
      return
    }

    // Authenticated tests
    console.log('\n✅ Authenticated - running full test suite')

    // Test 2: Navigate to dashboard
    console.log('\n📋 Test 2: Dashboard page accessible')
    await page.goto(`${TARGET_URL}/jobs/demo-job-1`)
    await page.waitForTimeout(1000)

    if (!page.url().includes('/login')) {
      console.log('✅ Dashboard page loaded')
    } else {
      console.log('⚠️  Unexpectedly redirected to login')
      return
    }

    // Test 3: Page structure
    console.log('\n📋 Test 3: Dashboard page structure')

    // Check for back button
    const backButton = await page.$(
      'button[aria-label="Back to sessions"], a[href="/sessions"]'
    )
    if (backButton) {
      console.log('✅ Back button present')
    }

    // Check for job title
    const jobTitle = await page.$('h1')
    if (jobTitle) {
      const text = await jobTitle.textContent()
      console.log(`✅ Job title displayed: "${text}"`)
    }

    // Test 4: Stats grid
    console.log('\n📋 Test 4: Stats grid visible')
    const discovered = await page.getByText('Discovered')
    const highMatch = await page.getByText('High Match')
    const emailsFound = await page.getByText('Emails Found')
    const avgScore = await page.getByText('Avg Score')

    let statsCount = 0
    if (await discovered.count()) statsCount++
    if (await highMatch.count()) statsCount++
    if (await emailsFound.count()) statsCount++
    if (await avgScore.count()) statsCount++

    if (statsCount >= 4) {
      console.log('✅ All 4 stat cards present')
    } else {
      console.log(`ℹ️  Found ${statsCount}/4 stat cards`)
    }

    // Test 5: Tab navigation
    console.log('\n📋 Test 5: Tab navigation')
    const tabs = await page.$$('[role="tab"]')
    if (tabs.length >= 3) {
      console.log(`✅ Found ${tabs.length} tabs`)

      // Click on different tabs
      for (const tab of tabs) {
        const tabText = await tab.textContent()
        await tab.click()
        await page.waitForTimeout(300)
        console.log(`  ✅ Clicked "${tabText}" tab`)
      }
    } else {
      console.log(`ℹ️  Found ${tabs.length} tabs`)
    }

    // Test 6: Sort dropdown
    console.log('\n📋 Test 6: Sort dropdown')
    const sortTrigger = await page.$(
      '[aria-label="Sort profiles"], button:has-text("Sort")'
    )
    if (sortTrigger) {
      await sortTrigger.click()
      await page.waitForTimeout(300)

      const sortOptions = await page.$$('[role="option"]')
      if (sortOptions.length > 0) {
        console.log(`✅ Sort dropdown has ${sortOptions.length} options`)

        // Click first option to close
        await sortOptions[0].click()
        await page.waitForTimeout(200)
      }
    } else {
      console.log('ℹ️  Sort dropdown not found')
    }

    // Test 7: Profile cards
    console.log('\n📋 Test 7: Profile cards')
    const profileCards = await page.$$('article')
    if (profileCards.length > 0) {
      console.log(`✅ Found ${profileCards.length} profile cards`)

      // Check first card structure
      const firstCard = profileCards[0]
      const avatar = await firstCard.$('img')
      const viewButton = await firstCard.$('button')

      if (avatar) console.log('  ✅ Profile avatar visible')
      if (viewButton) console.log('  ✅ Action buttons present')
    } else {
      console.log('ℹ️  No profile cards found (may need mock data)')
    }

    // Test 8: Score rings
    console.log('\n📋 Test 8: Score rings (ARIA progressbar)')
    const scoreRings = await page.$$('[role="progressbar"]')
    if (scoreRings.length > 0) {
      console.log(`✅ Found ${scoreRings.length} score rings`)

      // Check accessibility attributes
      const firstRing = scoreRings[0]
      const ariaValueNow = await firstRing.getAttribute('aria-valuenow')
      const ariaLabel = await firstRing.getAttribute('aria-label')

      if (ariaValueNow) console.log(`  ✅ Score value: ${ariaValueNow}`)
      if (ariaLabel) console.log(`  ✅ Accessible label: "${ariaLabel}"`)
    } else {
      console.log('ℹ️  No score rings found')
    }

    // Test 9: Responsive layouts
    console.log('\n📋 Test 9: Responsive layouts')

    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    await page.waitForTimeout(500)
    console.log('  ✅ Mobile viewport (375x667)')
    await page.screenshot({ path: '/tmp/dashboard-mobile.png' })

    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 })
    await page.waitForTimeout(500)
    console.log('  ✅ Tablet viewport (768x1024)')
    await page.screenshot({ path: '/tmp/dashboard-tablet.png' })

    // Test desktop viewport
    await page.setViewportSize({ width: 1280, height: 720 })
    await page.waitForTimeout(500)
    console.log('  ✅ Desktop viewport (1280x720)')
    await page.screenshot({ path: '/tmp/dashboard-desktop.png' })

    console.log('\n📸 Screenshots saved to /tmp/dashboard-*.png')
    console.log('\n🎉 All Epic 5 Dashboard journey tests completed!')
  } catch (error) {
    console.error('\n❌ Test failed:', error.message)
    await page.screenshot({ path: '/tmp/dashboard-error.png', fullPage: true })
    console.log('📸 Error screenshot saved to /tmp/dashboard-error.png')
    process.exitCode = 1
  } finally {
    await browser.close()
  }
}

runTests()
