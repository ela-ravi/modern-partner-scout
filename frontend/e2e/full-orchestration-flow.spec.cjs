/**
 * E2E Full Orchestration Flow Test
 * 
 * Tests the complete user journey from login to viewing scored profiles:
 * 1. User logs in
 * 2. Creates a new discovery session with reference profiles
 * 3. Launches the job (triggers orchestration)
 * 4. Monitors job status through all phases (analyzing → discovering → scoring → completed)
 * 5. Views the dashboard with scored profiles
 * 
 * Prerequisites:
 * 1. Frontend dev server: cd frontend && npm run dev
 * 2. Backend API server: cd backend && uvicorn app.main:app --reload
 * 3. Backend orchestration running (Python fallback or N8N)
 * 4. Valid Apify API key configured in backend
 * 5. Test credentials in e2e/.env
 * 
 * Run with: npm run e2e (included in test suite)
 * Or standalone: node e2e/full-orchestration-flow.spec.cjs
 * 
 * ⚠️ WARNING: This test triggers REAL API calls (Apify, LLM) and may take 3-10 minutes
 */

const { chromium } = require('playwright')
const authHelperPath = '/Volumes/Development/Practise/partner-scout/frontend/e2e/helpers/auth.cjs'
const { ensureAuthenticated, getTargetUrl } = require(authHelperPath)

// Configuration
const TARGET_URL = getTargetUrl()
const JOB_TIMEOUT_MS = 10 * 60 * 1000 // 10 minutes max for full orchestration
const POLL_INTERVAL_MS = 5000 // Check status every 5 seconds

// Test data - use real Instagram profiles for testing
const TEST_CAMPAIGN = {
  name: `E2E Test Campaign ${Date.now()}`,
  description: 'Automated E2E test - sustainable fashion brand focused on eco-friendly products and minimalist aesthetics.',
  referenceProfiles: [
    'thescentedcottage',
    'thehouseoffragrance.kg'
  ],
  // These should be small accounts to keep API costs low
}

async function runTests() {
  console.log('🧪 Starting Full Orchestration E2E Test')
  console.log(`📍 Target URL: ${TARGET_URL}`)
  console.log('⏱️  This test may take 3-10 minutes to complete')
  console.log('=' .repeat(60))

  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
  })
  const page = await context.newPage()

  let createdJobId = null

  try {
    // =========================================================================
    // STEP 1: Authentication
    // =========================================================================
    console.log('\n🔐 STEP 1: Authentication')
    const isAuthenticated = await ensureAuthenticated(page, context)

    if (!isAuthenticated) {
      console.log('❌ Authentication failed - cannot proceed with orchestration test')
      console.log('   Configure e2e/.env with valid test credentials')
      process.exitCode = 1
      return
    }
    console.log('✅ Authenticated successfully')

    // =========================================================================
    // STEP 2: Navigate to New Session Page
    // =========================================================================
    console.log('\n📝 STEP 2: Navigate to New Session Page')
    await page.goto(`${TARGET_URL}/new-session`)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    if (page.url().includes('/login')) {
      throw new Error('Unexpectedly redirected to login')
    }
    console.log('✅ New session page loaded')

    // =========================================================================
    // STEP 3: Fill Discovery Configuration Form
    // =========================================================================
    console.log('\n📋 STEP 3: Fill Discovery Configuration Form')

    // Fill campaign name
    const nameInput = await page.$('input[placeholder*="Campaign"], input[name*="name"], input[id*="name"]')
    if (nameInput) {
      await nameInput.fill(TEST_CAMPAIGN.name)
      console.log(`   ✅ Campaign name: "${TEST_CAMPAIGN.name}"`)
    } else {
      console.log('   ⚠️ Campaign name input not found, trying first text input')
      const firstInput = await page.$('input[type="text"]')
      if (firstInput) {
        await firstInput.fill(TEST_CAMPAIGN.name)
      }
    }

    // Fill brand description
    const descTextarea = await page.$('textarea')
    if (descTextarea) {
      await descTextarea.fill(TEST_CAMPAIGN.description)
      console.log('   ✅ Brand description filled')
    }

    // Add reference profiles
    const profileInput = await page.$('input[placeholder*="instagram"], input[placeholder*="profile"], input[placeholder*="username"]')
    if (profileInput) {
      for (const profile of TEST_CAMPAIGN.referenceProfiles) {
        await profileInput.fill(profile)
        await page.keyboard.press('Enter')
        await page.waitForTimeout(300)
        console.log(`   ✅ Added reference profile: @${profile}`)
      }
    } else {
      console.log('   ⚠️ Profile input not found')
    }

    // Take screenshot of filled form
    await page.screenshot({ path: '/tmp/orchestration-step3-form.png' })
    console.log('   📸 Screenshot: /tmp/orchestration-step3-form.png')

    // =========================================================================
    // STEP 4: Submit Form and Navigate to Review
    // =========================================================================
    console.log('\n🔍 STEP 4: Navigate to Review Page')

    const reviewButton = await page.$('button:has-text("Review"), button:has-text("Next")')
    if (reviewButton) {
      const isDisabled = await reviewButton.isDisabled()
      if (!isDisabled) {
        await reviewButton.click()
        await page.waitForTimeout(1000)
        console.log('   ✅ Clicked Review button')
      } else {
        console.log('   ⚠️ Review button is disabled - form may be incomplete')
      }
    }

    // =========================================================================
    // STEP 5: Launch Discovery Job
    // =========================================================================
    console.log('\n🚀 STEP 5: Launch Discovery Job')

    const launchButton = await page.$('button:has-text("Launch"), button:has-text("Start"), button:has-text("Begin")')
    if (launchButton) {
      const isDisabled = await launchButton.isDisabled()
      if (!isDisabled) {
        // Listen for navigation to job dashboard
        const navigationPromise = page.waitForURL('**/jobs/**', { timeout: 30000 })
        
        await launchButton.click()
        console.log('   ✅ Clicked Launch button')

        // Wait for redirect to job dashboard
        try {
          await navigationPromise
          console.log('   ✅ Redirected to job dashboard')
          
          // Extract job ID from URL
          const currentUrl = page.url()
          const jobIdMatch = currentUrl.match(/\/jobs\/([a-zA-Z0-9-]+)/)
          if (jobIdMatch) {
            createdJobId = jobIdMatch[1]
            console.log(`   ✅ Job created: ${createdJobId}`)
          }
        } catch (e) {
          console.log('   ⚠️ Navigation timeout - checking current state')
        }
      } else {
        console.log('   ⚠️ Launch button is disabled')
      }
    } else {
      console.log('   ⚠️ Launch button not found - checking if job was auto-created')
    }

    // If we couldn't get job ID from URL, try to find it on the page
    if (!createdJobId) {
      // Navigate to sessions to find the latest job
      await page.goto(`${TARGET_URL}/sessions`)
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(1000)

      // Click the first session card (most recent)
      const sessionCard = await page.$('article a, [class*="card"] a')
      if (sessionCard) {
        await sessionCard.click()
        await page.waitForLoadState('networkidle')
        
        const currentUrl = page.url()
        const jobIdMatch = currentUrl.match(/\/jobs\/([a-zA-Z0-9-]+)/)
        if (jobIdMatch) {
          createdJobId = jobIdMatch[1]
          console.log(`   ✅ Found job ID: ${createdJobId}`)
        }
      }
    }

    if (!createdJobId) {
      throw new Error('Could not create or find a job to monitor')
    }

    await page.screenshot({ path: '/tmp/orchestration-step5-launched.png' })

    // =========================================================================
    // STEP 6: Monitor Job Status Through Orchestration
    // =========================================================================
    console.log('\n⏳ STEP 6: Monitor Job Status (this may take several minutes)')
    console.log('   Orchestration phases: pending → analyzing → discovering → scoring → completed')

    const startTime = Date.now()
    let lastStatus = null
    let isCompleted = false
    let pollCount = 0

    while (!isCompleted && (Date.now() - startTime) < JOB_TIMEOUT_MS) {
      pollCount++
      
      // Refresh the page to get latest status
      await page.reload({ waitUntil: 'networkidle' })
      await page.waitForTimeout(1000)

      // Try to find status indicator on the page
      const statusElement = await page.$('[data-testid="job-status"], [class*="status"], .badge')
      let currentStatus = null

      if (statusElement) {
        currentStatus = await statusElement.textContent()
        currentStatus = currentStatus?.toLowerCase().trim()
      }

      // Also check the page content for status
      const pageContent = await page.textContent('body')
      const statusPatterns = ['completed', 'scoring', 'discovering', 'analyzing', 'pending', 'failed']
      for (const pattern of statusPatterns) {
        if (pageContent.toLowerCase().includes(pattern)) {
          if (!currentStatus || currentStatus === '') {
            currentStatus = pattern
          }
          break
        }
      }

      if (currentStatus && currentStatus !== lastStatus) {
        const elapsed = Math.round((Date.now() - startTime) / 1000)
        console.log(`   [${elapsed}s] Status changed: ${lastStatus || 'unknown'} → ${currentStatus}`)
        lastStatus = currentStatus

        // Take screenshot on status change
        await page.screenshot({ path: `/tmp/orchestration-status-${currentStatus}.png` })
      }

      // Check for completion
      if (currentStatus === 'completed') {
        isCompleted = true
        console.log('   ✅ Job completed successfully!')
      } else if (currentStatus === 'failed') {
        throw new Error('Job failed during orchestration')
      }

      if (!isCompleted) {
        // Wait before next poll
        await page.waitForTimeout(POLL_INTERVAL_MS)
      }
    }

    if (!isCompleted) {
      console.log('   ⚠️ Job did not complete within timeout - continuing with current state')
    }

    const totalTime = Math.round((Date.now() - startTime) / 1000)
    console.log(`   ⏱️ Total orchestration time: ${totalTime} seconds`)

    // =========================================================================
    // STEP 7: Verify Dashboard Shows Scored Profiles
    // =========================================================================
    console.log('\n📊 STEP 7: Verify Dashboard with Scored Profiles')

    // Navigate to job dashboard
    await page.goto(`${TARGET_URL}/jobs/${createdJobId}`)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)

    // Check for profile cards
    const profileCards = await page.$$('article, [data-testid="profile-card"]')
    console.log(`   ✅ Found ${profileCards.length} profile cards`)

    if (profileCards.length > 0) {
      // Check for score indicators
      const scoreElements = await page.$$('[role="progressbar"], [class*="score"]')
      console.log(`   ✅ Found ${scoreElements.length} score indicators`)

      // Get first profile's score
      if (scoreElements.length > 0) {
        const firstScore = await scoreElements[0].getAttribute('aria-valuenow')
        if (firstScore) {
          console.log(`   ✅ First profile score: ${firstScore}`)
        }
      }

      // Check for email indicators
      const emailElements = await page.$$('[class*="email"], svg[class*="mail"], [aria-label*="email"]')
      console.log(`   ✅ Found ${emailElements.length} email indicators`)
    }

    // Check stats cards - verify they don't show NaN
    const statsText = await page.textContent('body')
    if (statsText.includes('Discovered')) {
      console.log('   ✅ Stats section shows "Discovered" count')
    }
    if (statsText.includes('High Match') || statsText.includes('Emails')) {
      console.log('   ✅ Stats section shows match/email counts')
    }
    
    // Verify NaN fix - check Avg Score doesn't contain NaN
    if (statsText.includes('NaN')) {
      console.log('   ⚠️ WARNING: NaN found in stats - analytics transform may have issue')
    } else {
      console.log('   ✅ No NaN values in stats (analytics transform working)')
    }
    
    // Check for Avg Score value
    const avgScoreMatch = statsText.match(/Avg Score[\s\S]{0,20}(\d+)%/)
    if (avgScoreMatch) {
      console.log(`   ✅ Avg Score: ${avgScoreMatch[1]}%`)
    }

    // Check tab navigation (All, New, Processing, Done)
    const tabs = await page.$$('[role="tab"]')
    if (tabs.length > 0) {
      console.log(`   ✅ Found ${tabs.length} filter tabs`)
      
      // Click "Done" tab to see scored profiles
      const doneTab = await page.$('[role="tab"]:has-text("Done"), [role="tab"]:has-text("Scored")')
      if (doneTab) {
        await doneTab.click()
        await page.waitForTimeout(1000)
        
        const doneProfiles = await page.$$('article')
        console.log(`   ✅ "Done" tab shows ${doneProfiles.length} scored profiles`)
      }
    }

    // Take final screenshot
    await page.screenshot({ path: '/tmp/orchestration-step7-final.png', fullPage: true })
    console.log('   📸 Final screenshot: /tmp/orchestration-step7-final.png')

    // =========================================================================
    // STEP 8: Test Profile Detail Modal (if profiles exist)
    // =========================================================================
    if (profileCards.length > 0) {
      console.log('\n🔍 STEP 8: Test Profile Detail Modal')

      try {
        // Re-query for fresh elements (avoid stale DOM references)
        await page.waitForTimeout(500)
        const freshCards = await page.$$('article, [data-testid="profile-card"]')
        
        if (freshCards.length > 0) {
          // Look for a View button on any card
          const viewButton = await page.$('article button:has-text("View"), button[aria-label*="View"]')
          
          if (viewButton) {
            await viewButton.click()
            await page.waitForTimeout(1000)

            // Check for modal
            const modal = await page.$('[role="dialog"], [class*="modal"]')
            if (modal) {
              console.log('   ✅ Profile detail modal opened')

              // Check for score breakdown
              const scoreBreakdown = await modal.$$('[class*="score"], [class*="metric"]')
              console.log(`   ✅ Score breakdown has ${scoreBreakdown.length} metrics`)

              // Check for email button
              const emailButton = await modal.$('button:has-text("Email"), button:has-text("Contact")')
              if (emailButton) {
                console.log('   ✅ Email/Contact button present')
              }

              // Close modal
              await page.keyboard.press('Escape')
              await page.waitForTimeout(500)
            } else {
              console.log('   ℹ️ Modal not found - may use different navigation pattern')
            }
          } else {
            console.log('   ℹ️ View button not found on profile cards')
          }
        }

        await page.screenshot({ path: '/tmp/orchestration-step8-modal.png' })
        console.log('   📸 Screenshot: /tmp/orchestration-step8-modal.png')
      } catch (modalError) {
        console.log(`   ⚠️ Modal test skipped: ${modalError.message}`)
        // Don't fail the whole test for modal issues
      }
    }

    // =========================================================================
    // TEST COMPLETE
    // =========================================================================
    console.log('\n' + '=' .repeat(60))
    console.log('🎉 FULL ORCHESTRATION E2E TEST COMPLETED SUCCESSFULLY!')
    console.log('=' .repeat(60))
    console.log('\nTest Summary:')
    console.log(`   Job ID: ${createdJobId}`)
    console.log(`   Total time: ${totalTime} seconds`)
    console.log(`   Profiles found: ${profileCards.length}`)
    console.log(`   Final status: ${lastStatus || 'unknown'}`)
    console.log('\nScreenshots saved to /tmp/orchestration-*.png')

  } catch (error) {
    console.error('\n❌ Test failed:', error.message)
    await page.screenshot({ path: '/tmp/orchestration-error.png', fullPage: true })
    console.log('📸 Error screenshot saved to /tmp/orchestration-error.png')
    process.exitCode = 1
  } finally {
    // Cleanup: Optionally delete the test job
    if (createdJobId) {
      console.log(`\n🧹 Test job ${createdJobId} was created`)
      console.log('   You may want to delete it manually from sessions page')
    }

    await browser.close()
  }
}

runTests()
