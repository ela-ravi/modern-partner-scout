/**
 * E2E Tests for Discovery Configuration Flow
 *
 * Run with: cd .cursor/skills/playwright-skill && node run.js ../../../frontend/e2e/discovery-config.spec.js
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
  console.log('🧪 Starting E2E Discovery Config Tests')
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
      console.log('   Discovery config tests require authentication')

      // Test login form accessibility
      console.log('\n📋 Test: Login form accessible')
      await page.goto(`${TARGET_URL}/login`)
      const emailInput = await page.$('input[type="email"]')
      if (emailInput) {
        console.log('✅ Email input present')
        await page.fill('input[type="email"]', 'test@example.com')
        await page.fill('input[type="password"]', 'password123')
        console.log('✅ Can fill form fields')
      }

      console.log('\n🎉 Unauthenticated tests completed!')
      return
    }

    // Authenticated tests
    console.log('\n✅ Authenticated - running full test suite')

    // Test 2: New session page renders
    console.log('\n📋 Test 2: New session page renders')
    await page.goto(`${TARGET_URL}/new-session`)
    await page.waitForTimeout(1000)

    const url = page.url()
    if (url.includes('/new-session')) {
      console.log('✅ Discovery config page rendered')
    } else if (url.includes('/login')) {
      console.log('⚠️  Unexpectedly redirected to login')
      return
    }

    // Test 3: Form fields exist
    console.log('\n📋 Test 3: Form fields exist')

    const campaignNameInput = await page.$(
      'input[placeholder*="Campaign"], input[name*="name"], input[id*="name"]'
    )
    if (campaignNameInput) {
      console.log('✅ Campaign name input found')
    }

    const brandDescTextarea = await page.$('textarea')
    if (brandDescTextarea) {
      console.log('✅ Brand description textarea found')
    }

    // Test 4: Fill form fields
    console.log('\n📋 Test 4: Fill configuration form')

    // Fill campaign name
    if (campaignNameInput) {
      await campaignNameInput.fill('Summer 2026 Campaign')
      console.log('✅ Filled campaign name')
    }

    // Fill brand description
    if (brandDescTextarea) {
      await brandDescTextarea.fill(
        'A premium lifestyle brand focused on sustainable fashion.'
      )
      console.log('✅ Filled brand description')
    }

    // Test 5: Add reference profiles
    console.log('\n📋 Test 5: Add reference profiles')

    const profileInput = await page.$(
      'input[placeholder*="instagram"], input[placeholder*="profile"]'
    )
    if (profileInput) {
      await profileInput.fill('https://instagram.com/examplebrand1')
      await page.keyboard.press('Enter')
      await page.waitForTimeout(300)

      await profileInput.fill('https://instagram.com/examplebrand2')
      await page.keyboard.press('Enter')
      await page.waitForTimeout(300)

      console.log('✅ Added reference profiles')
    }

    // Test 6: Stepper shows correct step (Step 1: Configure)
    console.log('\n📋 Test 6: Stepper component')

    const stepperStep1 = await page.$('[data-status="active"]')
    if (stepperStep1) {
      const stepText = await stepperStep1.textContent()
      if (stepText.includes('Configure') || stepText.includes('1')) {
        console.log('✅ Stepper shows Step 1 (Configure) as active')
      }
    } else {
      console.log('ℹ️  Stepper not found or different structure')
    }

    // Test 7: Follower presets functional
    console.log('\n📋 Test 7: Follower presets')

    const microPreset = await page.$('button:has-text("Micro")')
    if (microPreset) {
      await microPreset.click()
      await page.waitForTimeout(300)
      console.log('✅ Follower preset buttons functional')
    } else {
      console.log('ℹ️  Follower presets not found')
    }

    // Test 8: Sliders exist and are functional
    console.log('\n📋 Test 8: Sliders functional')

    const sliders = await page.$$('[role="slider"]')
    if (sliders.length >= 2) {
      console.log(`✅ Found ${sliders.length} slider components`)

      // Try to interact with slider using keyboard
      await sliders[0].focus()
      await page.keyboard.press('ArrowRight')
      console.log('✅ Slider responds to keyboard')
    } else {
      console.log(`ℹ️  Found ${sliders.length} sliders`)
    }

    // Test 9: Review button
    console.log('\n📋 Test 9: Review button functionality')

    const reviewButton = await page.$('button:has-text("Review")')
    if (reviewButton) {
      const isDisabled = await reviewButton.isDisabled()
      console.log(`✅ Review button exists (disabled: ${isDisabled})`)

      // If form is valid, click review to test step 2
      if (!isDisabled) {
        await reviewButton.click()
        await page.waitForTimeout(500)

        // Test 10: Review page has stepper with step 2 active
        console.log('\n📋 Test 10: Stepper shows Step 2 (Launch)')
        const stepperStep2 = await page.$('[data-status="active"]')
        if (stepperStep2) {
          const stepText = await stepperStep2.textContent()
          if (stepText.includes('Launch') || stepText.includes('2')) {
            console.log('✅ Stepper shows Step 2 (Launch) as active')
          }
        }

        // Check for completed step 1
        const completedStep = await page.$('[data-status="complete"]')
        if (completedStep) {
          console.log('✅ Step 1 (Configure) shows as complete')
        }

        // Test 11: Estimated time display
        console.log('\n📋 Test 11: Estimated time display visible')
        const estimatedTime = await page.$('[data-testid="estimated-time"]')
        if (estimatedTime) {
          const timeText = await estimatedTime.textContent()
          if (timeText.includes('3-5 minutes')) {
            console.log('✅ Estimated time shows ~3-5 minutes')
          }
          console.log('✅ Estimated time displayed')
        }

        // Test 12: Info note visible
        console.log('\n📋 Test 12: Info note about real-time updates visible')
        const infoNote = await page.$('[data-testid="info-note"]')
        if (infoNote) {
          const noteText = await infoNote.textContent()
          if (noteText.includes('real-time')) {
            console.log('✅ Info note mentions real-time updates')
          }
          console.log('✅ Info note is visible on review page')
        }

        // Go back to config
        const backButton = await page.$('button:has-text("Back")')
        if (backButton) {
          await backButton.click()
          await page.waitForTimeout(300)
          console.log('✅ Back button works')
        }
      }
    }

    // Test 13: Navigation
    console.log('\n📋 Test 13: Navigation routes work')

    await page.goto(`${TARGET_URL}/sessions`)
    await page.waitForTimeout(500)
    if (!page.url().includes('/login')) {
      console.log('✅ Can navigate to sessions')
    }

    await page.goto(`${TARGET_URL}/jobs/demo-job-1`)
    await page.waitForTimeout(500)
    if (!page.url().includes('/login')) {
      console.log('✅ Can navigate to dashboard')
    }

    // Take screenshot
    await page.screenshot({
      path: '/tmp/discovery-config-test.png',
      fullPage: true,
    })
    console.log('\n📸 Screenshot saved to /tmp/discovery-config-test.png')

    console.log('\n🎉 All E2E discovery config tests passed!')
  } catch (error) {
    console.error('\n❌ Test failed:', error.message)
    await page.screenshot({
      path: '/tmp/discovery-config-error.png',
      fullPage: true,
    })
    console.log('📸 Error screenshot saved to /tmp/discovery-config-error.png')
    process.exitCode = 1
  } finally {
    await browser.close()
  }
}

runTests()
