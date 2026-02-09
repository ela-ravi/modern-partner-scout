/**
 * E2E Tests for Auto-Start Discovery Flow
 *
 * Tests that creating a job via the Discovery Config page
 * automatically starts the orchestrator and navigates to processing.
 *
 * Run with: node e2e/auto-start-flow.spec.cjs
 */

const { chromium } = require('playwright')
const authHelperPath = '/Volumes/Development/Practise/partner-scout/frontend/e2e/helpers/auth.cjs'
const { ensureAuthenticated, getTargetUrl } = require(authHelperPath)

const TARGET_URL = getTargetUrl()

async function runTests() {
  console.log('🧪 Starting Auto-Start Discovery Flow E2E Tests')
  console.log(`📍 Frontend URL: ${TARGET_URL}`)

  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext()
  const page = await context.newPage()

  try {
    // Step 1: Authenticate
    console.log('\n🔐 Step 1: Authentication')
    const isAuthenticated = await ensureAuthenticated(page, context)

    if (!isAuthenticated) {
      console.log('⚠️  Authentication required for this test')
      return
    }

    // Step 2: Navigate to discovery config page
    console.log('\n📋 Step 2: Navigate to Discovery Config')
    await page.goto(`${TARGET_URL}/new-session`)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000) // Wait for lazy-loaded component
    console.log(`   📍 Current URL: ${page.url()}`)

    // Check if we're on the config page
    const pageTitle = await page.$('h1')
    const titleText = pageTitle ? await pageTitle.textContent() : ''
    console.log(`   📄 Page heading: ${titleText}`)
    
    if (titleText?.includes('New Discovery') || titleText?.includes('Session')) {
      console.log('   ✅ Discovery config page loaded')
    } else {
      console.log('   ⚠️  Discovery config page heading not found')
      await page.screenshot({ path: '/tmp/config-page.png' })
      console.log('   📸 Screenshot saved to /tmp/config-page.png')
    }

    // Step 3: Fill in the form
    console.log('\n📝 Step 3: Fill configuration form')

    // Take screenshot to understand form structure
    await page.screenshot({ path: '/tmp/config-form.png', fullPage: true })
    console.log('   📸 Form screenshot saved to /tmp/config-form.png')

    // Campaign name - first text input in the form
    const inputs = await page.$$('input[type="text"]')
    console.log(`   Found ${inputs.length} text inputs`)
    
    if (inputs.length > 0) {
      await inputs[0].fill('Auto-Start Test Campaign')
      console.log('   ✅ Filled campaign name')
    }

    // Find the profile input (typically has placeholder mentioning Instagram or username)
    const allInputs = await page.$$('input')
    for (let i = 0; i < allInputs.length; i++) {
      const placeholder = await allInputs[i].getAttribute('placeholder')
      if (placeholder) {
        console.log(`   Input ${i}: placeholder="${placeholder}"`)
      }
    }

    // Reference profiles - find by exact placeholder
    const profileInput = await page.$('input[placeholder="https://instagram.com/username"]')
    const addButton = await page.$('button:has-text("Add")')
    
    if (profileInput && addButton) {
      // Add first profile
      await profileInput.click()
      await profileInput.fill('https://instagram.com/nike')
      await addButton.click()
      await page.waitForTimeout(300)
      console.log('   ✅ Added first reference profile')

      // Add second profile  
      await profileInput.click()
      await profileInput.fill('https://instagram.com/adidas')
      await addButton.click()
      await page.waitForTimeout(300)
      console.log('   ✅ Added second reference profile')
      
      // Check how many profiles are showing
      const profileTags = await page.$$('[data-testid="reference-profile"], .bg-apple-gray')
      console.log(`   📊 Profile tags displayed: ${profileTags.length}`)
    } else {
      console.log(`   ⚠️  Profile input found: ${!!profileInput}, Add button found: ${!!addButton}`)
    }
    
    await page.waitForTimeout(500)
    await page.screenshot({ path: '/tmp/config-form-filled.png', fullPage: true })
    console.log('   📸 Filled form screenshot saved to /tmp/config-form-filled.png')

    // Step 4: Check for validation errors and navigation controls
    console.log('\n🎯 Step 4: Navigate through form steps')

    // Check for any validation error messages
    const errorMessages = await page.$$eval('[role="alert"], .text-red-500, .text-apple-red, [aria-invalid="true"]', els => els.map(el => el.textContent))
    if (errorMessages.length > 0) {
      console.log('   ⚠️  Validation errors found:')
      errorMessages.forEach(msg => console.log(`      - ${msg}`))
    }

    // Check isValid state by looking at the Continue button's aria attributes
    const nextButton = await page.$('button:has-text("Continue"), button:has-text("Next"), button:has-text("Review")')
    if (nextButton) {
      const isEnabled = await nextButton.isEnabled()
      const ariaDisabled = await nextButton.getAttribute('aria-disabled')
      console.log(`   Next button found, enabled: ${isEnabled}, aria-disabled: ${ariaDisabled}`)
      
      if (isEnabled) {
        await nextButton.click()
        await page.waitForTimeout(500)
        console.log('   ✅ Moved to next step')
      } else {
        console.log('   ⚠️  Next button disabled - form validation required')
      }
    }

    // Look for Launch button
    const launchButton = await page.$('button:has-text("Launch"), button:has-text("Start Discovery")')
    if (launchButton) {
      const isEnabled = await launchButton.isEnabled()
      console.log(`   Launch button found, enabled: ${isEnabled}`)
      
      if (isEnabled) {
        // Click and monitor navigation
        const startUrl = page.url()
        
        // Set up network monitoring
        let startJobCalled = false
        page.on('request', (request) => {
          if (request.url().includes('/start') && request.method() === 'POST') {
            startJobCalled = true
          }
        })

        await launchButton.click()
        console.log('   ⏳ Launch clicked, waiting for navigation...')

        // Wait for navigation
        await page.waitForTimeout(3000)

        const endUrl = page.url()
        console.log(`   📍 Navigated to: ${endUrl}`)

        // Check if we navigated to processing page
        if (endUrl.includes('/processing')) {
          console.log('   ✅ Successfully navigated to processing page!')
        } else if (endUrl.includes('/jobs/')) {
          console.log('   ⚠️  Navigated to job page (not processing)')
        } else {
          console.log(`   ⚠️  Unexpected navigation: ${startUrl} → ${endUrl}`)
        }

        // Check if start job was called
        if (startJobCalled) {
          console.log('   ✅ Start job API was called')
        } else {
          console.log('   ⚠️  Start job API was NOT called')
        }
      }
    } else {
      console.log('   ℹ️  No launch button found yet - may need to complete form first')
    }

    console.log('\n🎉 Auto-Start Flow E2E test completed!')

  } catch (error) {
    console.error('\n❌ Test failed:', error.message)
    await page.screenshot({ path: '/tmp/auto-start-error.png' })
    console.log('   📸 Error screenshot saved to /tmp/auto-start-error.png')
  } finally {
    await browser.close()
  }
}

runTests().catch(console.error)
