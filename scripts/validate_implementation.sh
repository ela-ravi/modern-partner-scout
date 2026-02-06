#!/bin/bash
# ============================================================================
# Manual Validation Script for Items 1, 5, 8
# Run this AFTER applying the database migration
# ============================================================================

set -e

BASE_URL="http://localhost:8000"

# Generate test token
echo "🔐 Generating test token..."
cd /Volumes/Development/Practise/partner-scout/backend
source venv/bin/activate
TOKEN=$(python -c "
from app.guards.auth import create_test_token
from uuid import uuid4
print(create_test_token(str(uuid4()), 'test@example.com'))
")
cd - > /dev/null

echo ""
echo "=============================================="
echo "  VALIDATION: Item 5 - Job Creation Enhancements"
echo "=============================================="
echo ""

echo "📝 Creating job WITH new fields (keywords, hashtags, min_score_threshold)..."
JOB_RESPONSE=$(curl -s -X POST "$BASE_URL/api/jobs" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_description": "A sustainable eco-friendly fashion brand focused on organic materials",
    "reference_profiles": ["https://instagram.com/everlane", "https://instagram.com/patagonia"],
    "name": "Validation Test Job",
    "keywords": ["sustainable", "eco-friendly", "organic"],
    "hashtags": ["sustainablefashion", "ecofriendly"],
    "min_score_threshold": 70
  }')

echo "$JOB_RESPONSE" | jq '.'

# Extract job_id
JOB_ID=$(echo "$JOB_RESPONSE" | jq -r '.id')

if [ "$JOB_ID" == "null" ] || [ -z "$JOB_ID" ]; then
  echo ""
  echo "❌ FAILED: Could not create job. Check the error above."
  echo "   Did you apply the database migration?"
  exit 1
fi

echo ""
echo "✅ Job created with ID: $JOB_ID"
echo ""

# Verify fields
echo "🔍 Verifying new fields in response..."
KEYWORDS=$(echo "$JOB_RESPONSE" | jq -r '.keywords')
HASHTAGS=$(echo "$JOB_RESPONSE" | jq -r '.hashtags')
MIN_SCORE=$(echo "$JOB_RESPONSE" | jq -r '.min_score_threshold')

echo "   keywords: $KEYWORDS"
echo "   hashtags: $HASHTAGS"
echo "   min_score_threshold: $MIN_SCORE"

if [ "$MIN_SCORE" == "70" ]; then
  echo "✅ Item 5: PASSED - New fields are working!"
else
  echo "❌ Item 5: FAILED - Fields not returned correctly"
fi

echo ""
echo "=============================================="
echo "  VALIDATION: Item 1 - Cancel Job"
echo "=============================================="
echo ""

echo "🛑 Cancelling the job..."
CANCEL_RESPONSE=$(curl -s -X POST "$BASE_URL/api/jobs/$JOB_ID/cancel" \
  -H "Authorization: Bearer $TOKEN")

echo "$CANCEL_RESPONSE" | jq '.'

CANCEL_STATUS=$(echo "$CANCEL_RESPONSE" | jq -r '.status')

if [ "$CANCEL_STATUS" == "cancelled" ]; then
  echo ""
  echo "✅ Item 1: PASSED - Cancel endpoint works!"
else
  echo ""
  echo "❌ Item 1: FAILED - Cancel did not return 'cancelled' status"
fi

echo ""
echo "🔍 Trying to cancel again (should fail)..."
CANCEL_AGAIN=$(curl -s -X POST "$BASE_URL/api/jobs/$JOB_ID/cancel" \
  -H "Authorization: Bearer $TOKEN")

echo "$CANCEL_AGAIN" | jq '.'

echo ""
echo "=============================================="
echo "  VALIDATION: Item 8 - Demo Mode"
echo "=============================================="
echo ""

echo "🎬 Starting demo (anonymous)..."
DEMO_RESPONSE=$(curl -s -X POST "$BASE_URL/api/demo/start")

echo "$DEMO_RESPONSE" | jq '.'

IS_DEMO=$(echo "$DEMO_RESPONSE" | jq -r '.is_demo')
DEMO_JOB_ID=$(echo "$DEMO_RESPONSE" | jq -r '.job_id')
PROFILES_COUNT=$(echo "$DEMO_RESPONSE" | jq -r '.profiles_count')

if [ "$IS_DEMO" == "true" ] && [ "$PROFILES_COUNT" -gt "0" ]; then
  echo ""
  echo "✅ Item 8: PASSED - Demo mode works!"
  echo "   Created demo job: $DEMO_JOB_ID"
  echo "   Profiles created: $PROFILES_COUNT"
else
  echo ""
  echo "❌ Item 8: FAILED - Demo mode did not work correctly"
fi

echo ""
echo "=============================================="
echo "  SUMMARY"
echo "=============================================="
echo ""
echo "✅ Item 1 (Cancel Job): Check above"
echo "✅ Item 5 (Job Creation Enhancements): Check above"
echo "✅ Item 8 (Demo Mode): Check above"
echo ""
echo "🌐 View Swagger UI at: http://localhost:8000/docs"
echo ""
