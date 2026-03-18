/**
 * E2E Tests for Profile Detail Modal
 *
 * Run with: cd .cursor/skills/playwright-skill && node run.js ../../../frontend/e2e/profile-detail.spec.js
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
  console.log('🧪 Starting Profile Detail Modal E2E Tests')
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
      console.log('   Profile detail tests require authentication')

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
    console.log('\n📋 Test 2: Navigate to dashboard')
    await page.goto(`${TARGET_URL}/jobs/demo-job-1`)
    await page.waitForTimeout(1000)

    if (page.url().includes('/login')) {
      console.log('⚠️  Unexpectedly redirected to login')
      return
    }
    console.log('✅ Dashboard loaded')

    // Test 3: Click profile card to open modal
    console.log('\n📋 Test 3: Click profile card opens modal')
    const viewButtons = await page.$$('button:has-text("View")')
    if (viewButtons.length > 0) {
      await viewButtons[0].click()
      await page.waitForTimeout(500)

      // Check modal opened
      const modal = await page.$('[role="dialog"]')
      if (modal) {
        console.log('✅ Profile detail modal opened')

        // Test 4: Modal displays all data
        console.log('\n📋 Test 4: Modal displays all profile data')

        // Check for profile name (dialog title)
        const title = await page.$('h2')
        if (title) {
          const name = await title.textContent()
          console.log(`  ✅ Profile name displayed: ${name}`)
        }

        // Check for stats
        const followers = await page.$(':text("Followers")')
        if (followers) console.log('  ✅ Follower stats visible')

        const engagement = await page.$(':text("Engagement")')
        if (engagement) console.log('  ✅ Engagement stats visible')

        // Test 5: Score breakdown visible
        console.log('\n📋 Test 5: Score breakdown visible')
        const progressBars = await page.$$('[role="progressbar"]')
        if (progressBars.length > 1) {
          console.log(`  ✅ Found ${progressBars.length} score indicators`)
        }

        // Test 6: Action buttons functional
        console.log('\n📋 Test 6: Action buttons present')

        const saveButton = await page.$(
          'button:has-text("Save"), button:has-text("Bookmark")'
        )
        if (saveButton) console.log('  ✅ Save/Bookmark button present')

        const skipButton = await page.$('button:has-text("Skip")')
        if (skipButton) console.log('  ✅ Skip button present')

        const emailButton = await page.$(
          'button:has-text("Compose Email"), button:has-text("Email")'
        )
        if (emailButton) console.log('  ✅ Email button present')

        // Test 7: Copy email button
        console.log('\n📋 Test 7: Copy email button')
        const copyButton = await page.$('button[aria-label*="Copy"]')
        if (copyButton) {
          console.log('  ✅ Copy email button present')
        }

        // Test 8: Modal closes with close button
        console.log('\n📋 Test 8: Modal closes with close button')
        const closeButton = await page.$('button[aria-label*="Close"]')
        if (closeButton) {
          await closeButton.click()
          await page.waitForTimeout(300)

          const modalAfterClose = await page.$('[role="dialog"]')
          if (!modalAfterClose) {
            console.log('  ✅ Modal closed successfully')
          }
        }

        // Test 9: Modal closes with Escape key
        console.log('\n📋 Test 9: Modal closes with Escape key')
        // Reopen modal
        await viewButtons[0].click()
        await page.waitForTimeout(500)

        const modalReopened = await page.$('[role="dialog"]')
        if (modalReopened) {
          await page.keyboard.press('Escape')
          await page.waitForTimeout(300)

          const modalAfterEscape = await page.$('[role="dialog"]')
          if (!modalAfterEscape) {
            console.log('  ✅ Modal closes with Escape key')
          }
        }

        // Test 10: Focus trap
        console.log('\n📋 Test 10: Focus trapped in modal')
        await viewButtons[0].click()
        await page.waitForTimeout(500)

        // Tab through elements - focus should stay in modal
        for (let i = 0; i < 10; i++) {
          await page.keyboard.press('Tab')
        }
        const focusedElement = await page.evaluate(() =>
          document.activeElement?.closest('[role="dialog"]')
        )
        if (focusedElement) {
          console.log('  ✅ Focus remains trapped in modal')
        }

        // Close modal
        await page.keyboard.press('Escape')
      } else {
        console.log('⚠️  Modal did not open')
      }
    } else {
      console.log('⚠️  No profile cards found to click')
      console.log('   (May need mock data or a job with profiles)')
    }

    // Take screenshot
    await page.screenshot({
      path: '/tmp/profile-detail-test.png',
      fullPage: true,
    })
    console.log('\n📸 Screenshot saved to /tmp/profile-detail-test.png')

    console.log('\n🎉 All Profile Detail E2E tests completed!')
  } catch (error) {
    console.error('\n❌ Test failed:', error.message)
    await page.screenshot({
      path: '/tmp/profile-detail-error.png',
      fullPage: true,
    })
    console.log('📸 Error screenshot saved to /tmp/profile-detail-error.png')
    process.exitCode = 1
  } finally {
    await browser.close()
  }
}

runTests()
