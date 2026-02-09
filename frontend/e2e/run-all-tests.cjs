#!/usr/bin/env node
/**
 * E2E Test Runner for PartnerScout AI
 * 
 * Runs all Playwright E2E tests in sequence with proper error handling.
 * 
 * Usage:
 *   node e2e/run-all-tests.js
 *   node e2e/run-all-tests.js --headed  (run with visible browser)
 * 
 * Prerequisites:
 * 1. Frontend dev server running: npm run dev (port 5173)
 * 2. Backend API server running: uvicorn app.main:app (port 8000)
 * 3. Test credentials in e2e/.env (optional, for authenticated tests)
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Configuration
const HEADED = process.argv.includes('--headed');
const E2E_DIR = path.dirname(__filename);

// Load environment variables
function loadEnv() {
  const envPath = path.join(E2E_DIR, '.env');
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf8');
    for (const line of envContent.split('\n')) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) {
        const [key, ...valueParts] = trimmed.split('=');
        const value = valueParts.join('=').replace(/^["']|["']$/g, '');
        if (key && value) {
          process.env[key] = value;
        }
      }
    }
    console.log('📁 Loaded environment from e2e/.env');
  } else {
    console.log('⚠️  No e2e/.env found - running without credentials');
  }
}

// Test registry - ordered by dependency/flow
// Check if full orchestration test is requested
const RUN_ORCHESTRATION = process.argv.includes('--orchestration');

const TEST_SUITES = RUN_ORCHESTRATION ? [
  // Full orchestration test only (takes 3-10 minutes, triggers real API calls)
  { name: 'Full Orchestration Flow', file: 'full-orchestration-flow.spec.cjs', critical: true },
] : [
  // Quick UI tests (no real API calls)
  { name: 'Authentication', file: 'auth.spec.cjs', critical: true },
  { name: 'Sessions', file: 'sessions.spec.cjs', critical: true },
  { name: 'Discovery Config', file: 'discovery-config.spec.cjs', critical: true },
  { name: 'Dashboard', file: 'dashboard.spec.cjs', critical: true },
  { name: 'Pipeline', file: 'pipeline.spec.cjs', critical: false },
  { name: 'Profile Detail', file: 'profile-detail.spec.cjs', critical: false },
  { name: 'Email Composer', file: 'email-composer.spec.cjs', critical: false },
  { name: 'Epic 5 Dashboard Journey', file: 'epic5-dashboard-journey.spec.cjs', critical: false },
];

async function runTestFile(testPath, browser, context) {
  const page = await context.newPage();
  
  // Clear any module cache to ensure fresh require
  delete require.cache[require.resolve(testPath)];
  
  try {
    // Load and run the test module
    const testModule = require(testPath);
    
    // If the test exports a function, run it with the page
    if (typeof testModule === 'function') {
      await testModule(page, context, browser);
    } else if (typeof testModule.runTests === 'function') {
      await testModule.runTests(page, context, browser);
    } else {
      // The test is self-executing, just wait for it to complete
      // This is for tests that call their main function immediately
      console.log('   Test module executed on require');
    }
    
    return { success: true };
  } catch (error) {
    await page.screenshot({ 
      path: `/tmp/e2e-error-${path.basename(testPath, '.spec.js')}.png`,
      fullPage: true 
    });
    return { success: false, error: error.message };
  } finally {
    await page.close();
  }
}

async function runTestsSequentially(testFiles) {
  console.log('\\n🚀 Running E2E tests sequentially...');
  console.log(`   Mode: ${HEADED ? 'Headed (visible browser)' : 'Headless'}`);
  console.log(`   Tests to run: ${testFiles.length}\\n`);

  const browser = await chromium.launch({ headless: !HEADED });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
  });

  const results = [];

  for (const test of testFiles) {
    const testPath = path.join(E2E_DIR, test.file);
    
    if (!fs.existsSync(testPath)) {
      console.log(`⚠️  Skipping ${test.name}: File not found`);
      results.push({ name: test.name, status: 'skipped', reason: 'File not found' });
      continue;
    }

    console.log(`\\n${'='.repeat(60)}`);
    console.log(`📋 Running: ${test.name}`);
    console.log(`   File: ${test.file}`);
    console.log('='.repeat(60));

    const startTime = Date.now();
    
    try {
      // Execute the test file directly using a child process to maintain isolation
      const { spawn } = require('child_process');
      
      const result = await new Promise((resolve, reject) => {
        const proc = spawn('node', [testPath], {
          cwd: E2E_DIR,
          env: { ...process.env, HEADLESS: HEADED ? 'false' : 'true' },
          stdio: 'inherit',
        });
        
        proc.on('close', (code) => {
          resolve({ success: code === 0, exitCode: code });
        });
        
        proc.on('error', (err) => {
          reject(err);
        });
      });

      const duration = ((Date.now() - startTime) / 1000).toFixed(1);

      if (result.success) {
        console.log(`\\n✅ ${test.name} PASSED (${duration}s)`);
        results.push({ name: test.name, status: 'passed', duration });
      } else {
        console.log(`\\n❌ ${test.name} FAILED (exit code: ${result.exitCode}, ${duration}s)`);
        results.push({ name: test.name, status: 'failed', duration, exitCode: result.exitCode });
        
        if (test.critical) {
          console.log('\\n⚠️  Critical test failed - stopping test run');
          break;
        }
      }
    } catch (error) {
      const duration = ((Date.now() - startTime) / 1000).toFixed(1);
      console.log(`\\n❌ ${test.name} ERROR: ${error.message} (${duration}s)`);
      results.push({ name: test.name, status: 'error', duration, error: error.message });
      
      if (test.critical) {
        console.log('\\n⚠️  Critical test errored - stopping test run');
        break;
      }
    }
  }

  await browser.close();
  return results;
}

function printSummary(results) {
  console.log('\\n' + '='.repeat(60));
  console.log('📊 TEST SUMMARY');
  console.log('='.repeat(60));

  const passed = results.filter(r => r.status === 'passed').length;
  const failed = results.filter(r => r.status === 'failed').length;
  const errors = results.filter(r => r.status === 'error').length;
  const skipped = results.filter(r => r.status === 'skipped').length;

  for (const result of results) {
    const icon = {
      passed: '✅',
      failed: '❌',
      error: '💥',
      skipped: '⏭️',
    }[result.status];
    
    const duration = result.duration ? ` (${result.duration}s)` : '';
    console.log(`${icon} ${result.name}${duration}`);
  }

  console.log('\\n' + '-'.repeat(60));
  console.log(`Total: ${results.length} | ✅ Passed: ${passed} | ❌ Failed: ${failed} | 💥 Errors: ${errors} | ⏭️ Skipped: ${skipped}`);
  console.log('='.repeat(60));

  // Return exit code
  return failed + errors > 0 ? 1 : 0;
}

async function checkPrerequisites() {
  console.log('🔍 Checking prerequisites...');
  
  // Check if frontend is running
  try {
    const http = require('http');
    await new Promise((resolve, reject) => {
      const req = http.get('http://localhost:5173', (res) => {
        resolve(res.statusCode);
      });
      req.on('error', reject);
      req.setTimeout(2000, () => {
        req.destroy();
        reject(new Error('Timeout'));
      });
    });
    console.log('   ✅ Frontend server running on port 5173');
  } catch {
    console.log('   ❌ Frontend server not running on port 5173');
    console.log('   Run: cd frontend && npm run dev');
    return false;
  }

  // Check if backend is running
  try {
    const http = require('http');
    await new Promise((resolve, reject) => {
      const req = http.get('http://localhost:8000/api/health', (res) => {
        resolve(res.statusCode);
      });
      req.on('error', reject);
      req.setTimeout(2000, () => {
        req.destroy();
        reject(new Error('Timeout'));
      });
    });
    console.log('   ✅ Backend server running on port 8000');
  } catch {
    console.log('   ⚠️  Backend server may not be running on port 8000');
    console.log('   Some tests may fail without the backend');
  }

  return true;
}

async function main() {
  console.log('\\n🧪 PartnerScout AI - E2E Test Runner');
  console.log('=' .repeat(60));

  // Load environment
  loadEnv();

  // Check prerequisites
  const ready = await checkPrerequisites();
  if (!ready) {
    process.exit(1);
  }

  // Run tests
  const results = await runTestsSequentially(TEST_SUITES);

  // Print summary and exit
  const exitCode = printSummary(results);
  process.exit(exitCode);
}

main().catch((error) => {
  console.error('\\n💥 Fatal error:', error.message);
  process.exit(1);
});
