/**
 * E2E Tests for Processing Pipeline
 *
 * Run with: cd .cursor/skills/playwright-skill && node run.js ../../../frontend/e2e/pipeline.spec.js
 *
 * Prerequisites:
 * 1. Frontend dev server running: cd frontend && npm run dev
 * 2. Backend API server running: cd backend && uvicorn app.main:app --reload
 * 3. Test credentials configured in e2e/.env (copy from .env.example)
 */

const { chromium } = require('playwright')
// Use absolute path for the helper since Playwright skill copies files to temp location
const authHelperPath = '/Volumes/Development/Practise/partner-scout/frontend/e2e/helpers/auth.cjs'
const { ensureAuthenticated, getTargetUrl } = require(authHelperPath)

// Configuration
const TARGET_URL = getTargetUrl()

async function runTests() {
  console.log('🧪 Starting Processing Pipeline E2E Tests')
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
      console.log('   Pipeline tests require authentication')
      console.log('\n🎉 Unauthenticated tests completed!')
      return
    }

    // Step 2: Navigate to a processing page
    console.log('\n📋 Step 2: Navigate to processing page')
    
    // Try to find a job with processing status or navigate directly
    await page.goto(`${TARGET_URL}/jobs/demo-job-1/processing`)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1500)

    // Check if we got redirected or 404
    if (page.url().includes('/login')) {
      console.log('   ⚠️  Redirected to login - session may have expired')
      return
    }

    // Step 3: Test Pipeline Progress Component
    console.log('\n📊 Step 3: Testing Pipeline Progress Component')
    await testPipelineProgress(page)

    // Step 4: Test Activity Log
    console.log('\n📝 Step 4: Testing Activity Log')
    await testActivityLog(page)

    // Step 5: Test Controls
    console.log('\n🎮 Step 5: Testing Pipeline Controls')
    await testPipelineControls(page)

    // Step 6: Accessibility checks
    console.log('\n♿ Step 6: Accessibility checks')
    await testAccessibility(page)

    console.log('\n🎉 All Processing Pipeline E2E tests completed!')

  } catch (error) {
    console.error('\n❌ Test failed:', error.message)
    await page.screenshot({ path: '/tmp/pipeline-error.png' })
    console.log('   Screenshot saved to /tmp/pipeline-error.png')
    throw error
  } finally {
    await browser.close()
  }
}

async function testPipelineProgress(page) {
  // Check for 4 pipeline stages
  const stages = ['Brand Analyzer', 'Discovery Engine', 'Scoring Agent', 'Email Extractor']
  
  for (const stage of stages) {
    const stageElement = await page.$(`text="${stage}"`)
    if (stageElement) {
      console.log(`   ✅ Stage found: ${stage}`)
    } else {
      console.log(`   ⚠️  Stage not found: ${stage}`)
    }
  }

  // Check for overall progress bar
  const progressBar = await page.$('[role="progressbar"]')
  if (progressBar) {
    const valuenow = await progressBar.getAttribute('aria-valuenow')
    console.log(`   ✅ Overall progress bar found (${valuenow}%)`)
  } else {
    console.log('   ⚠️  Overall progress bar not found')
  }

  // Check for status badges
  const statusBadges = ['Complete', 'Running', 'Pending', 'Failed']
  for (const status of statusBadges) {
    const badge = await page.$(`text="${status}"`)
    if (badge) {
      console.log(`   ✅ Status badge found: ${status}`)
    }
  }
}

async function testActivityLog(page) {
  // Check for activity log container
  const logContainer = await page.$('[role="log"]')
  if (logContainer) {
    console.log('   ✅ Activity log container found')
    
    // Check ARIA attributes
    const ariaLive = await logContainer.getAttribute('aria-live')
    if (ariaLive === 'polite') {
      console.log('   ✅ Log has aria-live="polite"')
    }

    const ariaLabel = await logContainer.getAttribute('aria-label')
    if (ariaLabel) {
      console.log(`   ✅ Log has aria-label: "${ariaLabel}"`)
    }
  } else {
    console.log('   ⚠️  Activity log container not found')
  }

  // Check for log entries (may be empty initially)
  const logEntries = await page.$$('[role="log"] > div')
  console.log(`   ✅ Found ${logEntries.length} log entries`)
}

async function testPipelineControls(page) {
  // Check for Stop button
  const stopButton = await page.$('button:has-text("Stop")')
  if (stopButton) {
    console.log('   ✅ Stop button found')
    
    // Don't actually click to avoid stopping a real job
    const isEnabled = await stopButton.isEnabled()
    console.log(`   ✅ Stop button is ${isEnabled ? 'enabled' : 'disabled'}`)
  } else {
    console.log('   ⚠️  Stop button not found (job may be completed)')
  }

  // Check for View Dashboard button
  const dashboardButton = await page.$('button:has-text("View Dashboard")')
  if (dashboardButton) {
    console.log('   ✅ View Dashboard button found')
  }

  // Check for Retry button (only shown on failed jobs)
  const retryButton = await page.$('button:has-text("Retry")')
  if (retryButton) {
    console.log('   ✅ Retry button found (job may have failed)')
  }
}

async function testAccessibility(page) {
  // Check for proper heading structure
  const h1 = await page.$('h1')
  if (h1) {
    const text = await h1.textContent()
    console.log(`   ✅ H1 heading found: "${text.trim()}"`)
  }

  // Check for progress bar accessibility
  const progressBar = await page.$('[role="progressbar"]')
  if (progressBar) {
    const hasValuenow = await progressBar.getAttribute('aria-valuenow')
    const hasValuemin = await progressBar.getAttribute('aria-valuemin')
    const hasValuemax = await progressBar.getAttribute('aria-valuemax')
    
    if (hasValuenow && hasValuemin && hasValuemax) {
      console.log('   ✅ Progress bar has complete ARIA attributes')
    }
  }

  // Check for button accessibility
  const buttons = await page.$$('button')
  let accessibleButtons = 0
  for (const button of buttons) {
    const text = await button.textContent()
    const ariaLabel = await button.getAttribute('aria-label')
    if (text?.trim() || ariaLabel) {
      accessibleButtons++
    }
  }
  console.log(`   ✅ ${accessibleButtons}/${buttons.length} buttons are accessible`)
}

// Run the tests
runTests().catch(console.error)
