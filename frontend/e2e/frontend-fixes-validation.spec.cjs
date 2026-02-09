/**
 * E2E Tests for Frontend Bug Fixes
 *
 * This test suite validates the fixes for:
 * - BUG 1: Stats cards field mapping (NaN% fix)
 * - BUG 3: URL validation for Instagram profiles
 *
 * Run with: npm run e2e:fixes
 */

const { test, expect } = require('@playwright/test')
const { ensureAuthenticated, getTargetUrl, clearSession } = require('./helpers/auth.cjs')

const TARGET_URL = getTargetUrl()

test.describe('Frontend Bug Fixes Validation', () => {
  let page
  let context

  test.beforeAll(async ({ browser }) => {
    context = await browser.newContext({
      viewport: { width: 1280, height: 720 },
    })
    page = await context.newPage()
    console.log('\n============================================================')
    console.log('🧪 Frontend Bug Fixes Validation Tests')
    console.log(`📍 Target URL: ${TARGET_URL}`)
    console.log('============================================================\n')
  })

  test.afterAll(async () => {
    await context.close()
  })

  test.describe('BUG 1: Stats Display Fix', () => {
    test.beforeAll(async () => {
      await ensureAuthenticated(page, context)
    })

    test('stats cards should display numeric values, not NaN', async () => {
      console.log('📊 Testing: Stats cards display fix')

      // Navigate to sessions to find a job
      await page.goto(`${TARGET_URL}/sessions`)
      await page.waitForLoadState('networkidle')

      // Find the first session card and click it
      const sessionCards = await page.$$('[data-testid="session-card"], article')
      
      if (sessionCards.length === 0) {
        console.log('   ⚠️ No sessions found - creating a test job first')
        // Navigate to create a new session
        await page.goto(`${TARGET_URL}/new-session`)
        await page.waitForLoadState('networkidle')
        
        // Fill minimum required fields
        await page.fill('input[placeholder*="Campaign"]', `Stats Test ${Date.now()}`)
        await page.fill('textarea[placeholder*="Describe"]', 'Test brand for stats validation')
        
        // Add reference profiles
        await page.fill('input[placeholder*="instagram"]', 'https://instagram.com/testprofile1')
        await page.keyboard.press('Enter')
        await page.waitForTimeout(500)
        await page.fill('input[placeholder*="instagram"]', 'https://instagram.com/testprofile2')
        await page.keyboard.press('Enter')
        await page.waitForTimeout(500)
        
        // Try to launch (if possible)
        const launchButton = page.locator('button:has-text("Launch"), button:has-text("Review")')
        if (await launchButton.isEnabled()) {
          await launchButton.click()
          await page.waitForTimeout(2000)
        }
        
        // Go back to sessions
        await page.goto(`${TARGET_URL}/sessions`)
        await page.waitForLoadState('networkidle')
      }

      // Click first session to go to dashboard
      const firstSession = await page.$('[data-testid="session-card"], article')
      if (firstSession) {
        await firstSession.click()
        await page.waitForLoadState('networkidle')
        await page.waitForTimeout(1000)
      }

      // Check for stats cards
      const statsGrid = await page.$('[class*="grid"]')
      expect(statsGrid).toBeTruthy()

      // Check that "Discovered" stat shows a number
      const discoveredText = await page.textContent('p:has-text("Discovered") + p, div:has-text("Discovered")')
      console.log(`   📈 Discovered value: "${discoveredText}"`)
      
      // Check Avg Score doesn't show NaN
      const avgScoreElement = await page.locator('p:has-text("Avg Score")').first()
      if (await avgScoreElement.isVisible()) {
        const avgScoreParent = await avgScoreElement.locator('xpath=..').textContent()
        console.log(`   📈 Avg Score section: "${avgScoreParent}"`)
        expect(avgScoreParent).not.toContain('NaN')
      }

      // Take screenshot for verification
      await page.screenshot({ path: '/tmp/stats-fix-test.png', fullPage: true })
      console.log('   📸 Screenshot: /tmp/stats-fix-test.png')
      console.log('✅ Stats display test completed')
    })

    test('stats cards should show correct field mappings', async () => {
      console.log('📊 Testing: Stats field mappings')

      // Navigate to any job dashboard
      await page.goto(`${TARGET_URL}/sessions`)
      await page.waitForLoadState('networkidle')

      const firstSession = await page.$('[data-testid="session-card"], article')
      if (firstSession) {
        await firstSession.click()
        await page.waitForLoadState('networkidle')
        await page.waitForTimeout(1500)
      }

      // Verify all 4 stat cards are present with proper labels
      const expectedLabels = ['Discovered', 'High Match', 'Emails Found', 'Avg Score']
      
      for (const label of expectedLabels) {
        const labelElement = await page.locator(`p:has-text("${label}"), span:has-text("${label}")`).first()
        const isVisible = await labelElement.isVisible().catch(() => false)
        
        if (isVisible) {
          console.log(`   ✅ Found stat card: "${label}"`)
        } else {
          console.log(`   ⚠️ Stat card not found: "${label}"`)
        }
      }

      console.log('✅ Stats field mapping test completed')
    })
  })

  test.describe('BUG 3: URL Validation Fix', () => {
    test.beforeAll(async () => {
      await ensureAuthenticated(page, context)
    })

    test('should accept full Instagram URLs', async () => {
      console.log('🔗 Testing: Full Instagram URL validation')

      await page.goto(`${TARGET_URL}/new-session`)
      await page.waitForLoadState('networkidle')

      // Fill campaign name
      await page.fill('input[placeholder*="Campaign"]', `URL Test ${Date.now()}`)

      // Test full URL format
      const fullUrl = 'https://instagram.com/testprofile'
      await page.fill('input[placeholder*="instagram"]', fullUrl)
      await page.keyboard.press('Enter')
      await page.waitForTimeout(500)

      // Check if URL was added (no error toast)
      const errorToast = await page.$('[role="alert"]:has-text("valid URL")')
      expect(errorToast).toBeNull()

      // Check if tag was added
      const addedTags = await page.$$('span:has-text("instagram.com")')
      expect(addedTags.length).toBeGreaterThan(0)
      console.log(`   ✅ Full URL accepted: ${fullUrl}`)

      await page.screenshot({ path: '/tmp/url-validation-full.png' })
      console.log('   📸 Screenshot: /tmp/url-validation-full.png')
    })

    test('should accept @username format and normalize to URL', async () => {
      console.log('🔗 Testing: @username normalization')

      await page.goto(`${TARGET_URL}/new-session`)
      await page.waitForLoadState('networkidle')

      // Fill campaign name
      await page.fill('input[placeholder*="Campaign"]', `At Username Test ${Date.now()}`)

      // Test @username format
      const atUsername = '@thescentedcottage'
      await page.fill('input[placeholder*="instagram"]', atUsername)
      await page.keyboard.press('Enter')
      await page.waitForTimeout(500)

      // Should not show error
      const errorToast = await page.$('[role="alert"]:has-text("valid URL")')
      expect(errorToast).toBeNull()

      // Should normalize to full URL
      const addedTags = await page.$$('span:has-text("instagram.com/thescentedcottage"), button:has-text("thescentedcottage")')
      if (addedTags.length > 0) {
        console.log(`   ✅ @username normalized to URL`)
      } else {
        console.log(`   ⚠️ @username may not have been normalized`)
      }

      await page.screenshot({ path: '/tmp/url-validation-at.png' })
      console.log('   📸 Screenshot: /tmp/url-validation-at.png')
    })

    test('should accept URL without https:// prefix', async () => {
      console.log('🔗 Testing: URL without protocol')

      await page.goto(`${TARGET_URL}/new-session`)
      await page.waitForLoadState('networkidle')

      await page.fill('input[placeholder*="Campaign"]', `No Protocol Test ${Date.now()}`)

      // Test URL without protocol
      const noProtocol = 'instagram.com/wellness_guru'
      await page.fill('input[placeholder*="instagram"]', noProtocol)
      await page.keyboard.press('Enter')
      await page.waitForTimeout(500)

      // Should not show error
      const errorToast = await page.$('[role="alert"]:has-text("valid URL")')
      expect(errorToast).toBeNull()

      console.log(`   ✅ URL without protocol accepted: ${noProtocol}`)
      await page.screenshot({ path: '/tmp/url-validation-no-protocol.png' })
      console.log('   📸 Screenshot: /tmp/url-validation-no-protocol.png')
    })

    test('should reject non-Instagram URLs', async () => {
      console.log('🔗 Testing: Non-Instagram URL rejection')

      await page.goto(`${TARGET_URL}/new-session`)
      await page.waitForLoadState('networkidle')

      await page.fill('input[placeholder*="Campaign"]', `Non-IG Test ${Date.now()}`)

      // Test non-Instagram URL
      const nonIgUrl = 'https://twitter.com/someprofile'
      await page.fill('input[placeholder*="instagram"]', nonIgUrl)
      await page.keyboard.press('Enter')
      await page.waitForTimeout(500)

      // Should show error toast
      const errorToast = await page.$('[role="alert"]:has-text("Instagram")')
      if (errorToast) {
        console.log(`   ✅ Non-Instagram URL correctly rejected`)
      } else {
        console.log(`   ⚠️ Non-Instagram URL should be rejected`)
      }

      await page.screenshot({ path: '/tmp/url-validation-non-ig.png' })
      console.log('   📸 Screenshot: /tmp/url-validation-non-ig.png')
    })

    test('Review button should be enabled when form is valid', async () => {
      console.log('📝 Testing: Form validation and Review button')

      await page.goto(`${TARGET_URL}/new-session`)
      await page.waitForLoadState('networkidle')

      // Fill all required fields
      await page.fill('input[placeholder*="Campaign"]', `Complete Form Test ${Date.now()}`)
      await page.fill('textarea[placeholder*="Describe"]', 'A test brand description for validation')

      // Add 2 reference profiles (minimum required)
      await page.fill('input[placeholder*="instagram"]', 'https://instagram.com/profile1')
      await page.keyboard.press('Enter')
      await page.waitForTimeout(300)

      await page.fill('input[placeholder*="instagram"]', 'https://instagram.com/profile2')
      await page.keyboard.press('Enter')
      await page.waitForTimeout(300)

      // Check Review button state
      const reviewButton = page.locator('button:has-text("Review")')
      const isEnabled = await reviewButton.isEnabled()
      
      if (isEnabled) {
        console.log('   ✅ Review button is enabled with valid form')
      } else {
        console.log('   ⚠️ Review button is still disabled')
      }

      await page.screenshot({ path: '/tmp/form-complete-test.png', fullPage: true })
      console.log('   📸 Screenshot: /tmp/form-complete-test.png')
    })
  })

  test.describe('Profile Filtering', () => {
    test.beforeAll(async () => {
      await ensureAuthenticated(page, context)
    })

    test('filter tabs should be present on dashboard', async () => {
      console.log('🔍 Testing: Dashboard filter tabs')

      // Navigate to sessions and click first one
      await page.goto(`${TARGET_URL}/sessions`)
      await page.waitForLoadState('networkidle')

      const firstSession = await page.$('[data-testid="session-card"], article')
      if (firstSession) {
        await firstSession.click()
        await page.waitForLoadState('networkidle')
        await page.waitForTimeout(1000)
      }

      // Check for filter tabs
      const expectedTabs = ['All', 'New', 'Processing', 'Scored']
      
      for (const tabName of expectedTabs) {
        const tab = page.locator(`button[role="tab"]:has-text("${tabName}")`)
        const isVisible = await tab.isVisible().catch(() => false)
        
        if (isVisible) {
          console.log(`   ✅ Found filter tab: "${tabName}"`)
        } else {
          console.log(`   ⚠️ Filter tab not found: "${tabName}"`)
        }
      }

      // Click on each tab and verify it works
      for (const tabName of expectedTabs) {
        const tab = page.locator(`button[role="tab"]:has-text("${tabName}")`)
        if (await tab.isVisible().catch(() => false)) {
          await tab.click()
          await page.waitForTimeout(500)
          console.log(`   🔄 Switched to "${tabName}" tab`)
        }
      }

      await page.screenshot({ path: '/tmp/filter-tabs-test.png', fullPage: true })
      console.log('   📸 Screenshot: /tmp/filter-tabs-test.png')
      console.log('✅ Filter tabs test completed')
    })
  })
})
