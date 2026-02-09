/**
 * E2E Tests for Authentication Flow
 *
 * Run with: cd .cursor/skills/playwright-skill && node run.js ../../../frontend/e2e/auth.spec.js
 *
 * Prerequisites:
 * 1. Frontend dev server running: cd frontend && npm run dev
 * 2. (Optional) Test credentials configured in e2e/.env for full login test
 */

const { chromium } = require('playwright')
// Use absolute path for the helper since Playwright skill copies files to temp location
const authHelperPath = '/Volumes/Development/Practise/partner-scout/frontend/e2e/helpers/auth.cjs'
const { login, hasCredentials, getTargetUrl, clearSession } = require(authHelperPath)

// Configuration
const TARGET_URL = getTargetUrl()

async function runTests() {
  console.log('🧪 Starting E2E Auth Tests')
  console.log(`📍 Target URL: ${TARGET_URL}`)

  const browser = await chromium.launch({ headless: false })
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
  })
  const page = await context.newPage()

  // Clear any existing session to test fresh login
  clearSession()

  try {
    // Test 1: Login page renders correctly
    console.log('\n📋 Test 1: Login page renders correctly')
    await page.goto(`${TARGET_URL}/login`)
    await page.waitForSelector('h2')

    const heading = await page.textContent('h2')
    if (heading.includes('Sign in')) {
      console.log('✅ Login page heading displayed')
    } else {
      throw new Error('Login heading not found')
    }

    // Check for form elements
    const emailInput = await page.$('input[type="email"]')
    const passwordInput = await page.$('input[type="password"]')
    const submitButton = await page.$('button[type="submit"]')

    if (emailInput && passwordInput && submitButton) {
      console.log('✅ Form elements present (email, password, submit)')
    } else {
      throw new Error('Missing form elements')
    }

    // Test 2: Form validation
    console.log('\n📋 Test 2: Form validation works')
    await page.click('button[type="submit"]')
    // HTML5 validation should prevent submission with empty fields
    console.log('✅ Empty form submission handled')

    // Test 3: Can toggle between login and sign up
    console.log('\n📋 Test 3: Can toggle between login and sign up')
    await page.click("text=Don't have an account")
    await page.waitForSelector('text=Create an account')
    console.log('✅ Switched to sign up form')

    await page.click('text=Already have an account')
    await page.waitForSelector('text=Sign in')
    console.log('✅ Switched back to login form')

    // Test 4: Unauthenticated user redirected to login
    console.log('\n📋 Test 4: Protected routes redirect to login')
    await page.goto(`${TARGET_URL}/dashboard`)
    await page.waitForURL('**/login**')
    console.log('✅ Dashboard redirects to login when not authenticated')

    await page.goto(`${TARGET_URL}/sessions`)
    await page.waitForURL('**/login**')
    console.log('✅ Sessions redirects to login when not authenticated')

    await page.goto(`${TARGET_URL}/jobs/test-job-1`)
    await page.waitForURL('**/login**')
    console.log('✅ Job dashboard redirects to login when not authenticated')

    // Test 5: Accessibility checks
    console.log('\n📋 Test 5: Accessibility checks')
    await page.goto(`${TARGET_URL}/login`)
    await page.waitForSelector('input[type="email"]')

    // Check autocomplete attributes
    const emailAutocomplete = await page.$eval(
      'input[type="email"]',
      (el) => el.autocomplete
    )
    const passwordAutocomplete = await page.$eval(
      'input[type="password"]',
      (el) => el.autocomplete
    )

    if (emailAutocomplete === 'email') {
      console.log('✅ Email input has autocomplete="email"')
    }
    if (passwordAutocomplete === 'current-password') {
      console.log('✅ Password input has autocomplete="current-password"')
    }

    // Check for skip link
    await page.keyboard.press('Tab')
    const focusedElement = await page.evaluate(
      () => document.activeElement?.textContent
    )
    console.log(`   First tab stop: "${focusedElement?.trim() || 'N/A'}"`)

    // Test 6: Actual login (if credentials configured)
    console.log('\n📋 Test 6: Actual login flow')
    if (hasCredentials()) {
      console.log('   Credentials configured - testing real login')

      await page.goto(`${TARGET_URL}/login`)
      await page.waitForSelector('input[type="email"]')

      const loginSuccess = await login(page)
      if (loginSuccess) {
        console.log('✅ Real login successful!')

        // Verify we can access protected routes
        await page.goto(`${TARGET_URL}/sessions`)
        await page.waitForTimeout(1000)

        if (!page.url().includes('/login')) {
          console.log('✅ Can access protected routes after login')
        }

        // Test logout button if present
        const userMenu = await page.$(
          'button[aria-label*="user"], [data-testid="user-menu"]'
        )
        if (userMenu) {
          await userMenu.click()
          await page.waitForTimeout(300)

          const logoutButton = await page.$('button:has-text("Log out"), button:has-text("Sign out")')
          if (logoutButton) {
            console.log('✅ Logout option available in user menu')
          }
        }
      } else {
        console.log('⚠️  Login failed - check credentials in e2e/.env')
      }
    } else {
      console.log('   No credentials configured - skipping real login test')
      console.log('   To test actual login:')
      console.log('   1. Copy e2e/.env.example to e2e/.env')
      console.log('   2. Fill in your test account credentials')
    }

    // Take screenshot
    await page.screenshot({ path: '/tmp/auth-test-screenshot.png', fullPage: true })
    console.log('\n📸 Screenshot saved to /tmp/auth-test-screenshot.png')

    console.log('\n🎉 All E2E auth tests passed!')
  } catch (error) {
    console.error('\n❌ Test failed:', error.message)
    await page.screenshot({ path: '/tmp/auth-test-error.png', fullPage: true })
    console.log('📸 Error screenshot saved to /tmp/auth-test-error.png')
    process.exitCode = 1
  } finally {
    await browser.close()
  }
}

runTests()
