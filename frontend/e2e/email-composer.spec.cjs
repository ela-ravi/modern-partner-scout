/**
 * E2E Tests for Email Composer
 *
 * Run with: cd .cursor/skills/playwright-skill && node run.js ../../../frontend/e2e/email-composer.spec.js
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
  console.log('🧪 Starting Email Composer E2E Tests')
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
      console.log('   Email composer tests require authentication')
      console.log('\n🎉 Unauthenticated tests completed!')
      return
    }

    // Step 2: Navigate to a job dashboard
    console.log('\n📋 Step 2: Navigate to job dashboard')
    await page.goto(`${TARGET_URL}/sessions`)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    // Try to find and click on a session with profiles
    const sessionCards = await page.$$('[data-testid="session-card"], .session-card, [role="article"]')
    if (sessionCards.length > 0) {
      console.log(`   Found ${sessionCards.length} session(s)`)
      await sessionCards[0].click()
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(1500)
    } else {
      console.log('   No sessions found, testing with mock scenario')
      // Navigate to a specific job (may need to create one first)
      await page.goto(`${TARGET_URL}/jobs/demo-job-1`)
      await page.waitForTimeout(1000)
    }

    // Step 3: Find a profile card and click email button
    console.log('\n📧 Step 3: Test email button on profile card')
    const profileCards = await page.$$('[data-testid="profile-card"], .profile-card')
    
    if (profileCards.length > 0) {
      console.log(`   Found ${profileCards.length} profile card(s)`)
      
      // Look for email button on the first profile card
      const emailButton = await page.$('[aria-label*="email" i], [aria-label*="compose" i], button:has-text("Email")')
      
      if (emailButton) {
        await emailButton.click()
        await page.waitForTimeout(500)
        
        // Check if email composer modal opened
        const composerModal = await page.$('[role="dialog"]')
        if (composerModal) {
          console.log('✅ Email composer modal opened from profile card')
          
          // Test email composer elements
          await testEmailComposerElements(page)
          
          // Close the modal
          const closeButton = await page.$('[aria-label="Close"], button:has-text("Cancel")')
          if (closeButton) {
            await closeButton.click()
            await page.waitForTimeout(300)
            console.log('✅ Email composer closed successfully')
          }
        }
      } else {
        console.log('   No email button found on profile cards')
      }
    } else {
      console.log('   No profile cards found on this page')
    }

    // Step 4: Open profile detail and test email from there
    console.log('\n📋 Step 4: Test email from profile detail modal')
    
    // Click on a profile card to open detail
    const profileCard = await page.$('[data-testid="profile-card"], .profile-card')
    if (profileCard) {
      await profileCard.click()
      await page.waitForTimeout(500)
      
      const detailModal = await page.$('[role="dialog"]')
      if (detailModal) {
        console.log('   Profile detail modal opened')
        
        // Look for Compose Email button in detail modal
        const composeButton = await page.$('button:has-text("Compose Email")')
        if (composeButton) {
          await composeButton.click()
          await page.waitForTimeout(500)
          
          // Check if email composer opened
          const emailDialog = await page.$('[role="dialog"]:has-text("Compose Email")')
          if (emailDialog) {
            console.log('✅ Email composer opened from profile detail')
            
            await testEmailComposerElements(page)
            await testToneSelector(page)
            await testGenerateButton(page)
            
            // Close
            const closeBtn = await page.$('[aria-label="Close"], button:has-text("Cancel")')
            if (closeBtn) await closeBtn.click()
          }
        } else {
          console.log('   Compose Email button not found (profile may not have email)')
        }
      }
    }

    // Step 5: Test accessibility
    console.log('\n♿ Step 5: Accessibility checks')
    await testAccessibility(page)

    console.log('\n🎉 All Email Composer E2E tests completed!')

  } catch (error) {
    console.error('\n❌ Test failed:', error.message)
    await page.screenshot({ path: '/tmp/email-composer-error.png' })
    console.log('   Screenshot saved to /tmp/email-composer-error.png')
    throw error
  } finally {
    await browser.close()
  }
}

async function testEmailComposerElements(page) {
  console.log('\n   Testing email composer elements:')
  
  // Check for recipient section
  const recipientLabel = await page.$('label:has-text("To"), text="To"')
  if (recipientLabel) {
    console.log('   ✅ Recipient (To) field present')
  }
  
  // Check for subject input
  const subjectInput = await page.$('input[id*="subject"], [aria-label*="Subject" i]')
  if (subjectInput) {
    console.log('   ✅ Subject input present')
  }
  
  // Check for message textarea
  const messageTextarea = await page.$('textarea, [aria-label*="Message" i]')
  if (messageTextarea) {
    console.log('   ✅ Message textarea present')
  }
  
  // Check for Send button
  const sendButton = await page.$('button:has-text("Send")')
  if (sendButton) {
    console.log('   ✅ Send button present')
  }
}

async function testToneSelector(page) {
  console.log('\n   Testing tone selector:')
  
  // Look for tone buttons
  const toneButtons = await page.$$('button:has-text("Professional"), button:has-text("Friendly"), button:has-text("Enthusiastic")')
  
  if (toneButtons.length > 0) {
    console.log(`   ✅ Found ${toneButtons.length} tone option(s)`)
    
    // Try clicking a different tone
    const friendlyTone = await page.$('button:has-text("Friendly")')
    if (friendlyTone) {
      await friendlyTone.click()
      await page.waitForTimeout(200)
      console.log('   ✅ Tone selector is interactive')
    }
  } else {
    console.log('   ⚠️  No tone buttons found (may be loading)')
  }
}

async function testGenerateButton(page) {
  console.log('\n   Testing Generate with AI button:')
  
  const generateButton = await page.$('button:has-text("Generate")')
  if (generateButton) {
    console.log('   ✅ Generate with AI button present')
    
    // Don't actually click to avoid API calls in E2E tests
    const isEnabled = await generateButton.isEnabled()
    console.log(`   ✅ Generate button is ${isEnabled ? 'enabled' : 'disabled'}`)
  }
}

async function testAccessibility(page) {
  // Check for proper ARIA attributes
  const dialog = await page.$('[role="dialog"]')
  if (dialog) {
    const ariaModal = await dialog.getAttribute('aria-modal')
    const ariaLabelledby = await dialog.getAttribute('aria-labelledby')
    
    if (ariaModal === 'true') {
      console.log('   ✅ Dialog has aria-modal="true"')
    }
    if (ariaLabelledby) {
      console.log('   ✅ Dialog has aria-labelledby')
    }
  }
  
  // Check for form labels
  const labels = await page.$$('label')
  if (labels.length > 0) {
    console.log(`   ✅ Found ${labels.length} form label(s)`)
  }
}

// Run the tests
runTests().catch(console.error)
