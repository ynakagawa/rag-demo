#!/bin/bash

# Test AEM Connectivity Script
# This script tests your AEM credentials and connectivity

# Load environment variables
source .env

AEM_SERVER="${AEM_SERVER:-https://author-p18253-e46622.adobeaemcloud.com}"
AEM_TOKEN="${AEM_TOKEN}"

echo "🔍 Testing AEM Connectivity"
echo "================================"
echo ""
echo "AEM Server: $AEM_SERVER"
echo "Token: ${AEM_TOKEN:0:50}... (truncated for display)"
echo ""

# Test 1: Basic connectivity
echo "Test 1: Basic Connectivity"
echo "---------------------------"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $AEM_TOKEN" \
  "$AEM_SERVER/api/sites.json")

if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Success! HTTP Status: $HTTP_CODE"
elif [ "$HTTP_CODE" = "401" ]; then
  echo "❌ Authentication Failed! HTTP Status: $HTTP_CODE"
  echo "   Your AEM token may be expired or invalid."
elif [ "$HTTP_CODE" = "403" ]; then
  echo "⚠️  Forbidden! HTTP Status: $HTTP_CODE"
  echo "   Your token is valid but lacks permissions."
else
  echo "❌ Failed! HTTP Status: $HTTP_CODE"
fi
echo ""

# Test 2: List Sites (what the MCP tool does)
echo "Test 2: List AEM Sites"
echo "----------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  -H "Authorization: Bearer $AEM_TOKEN" \
  -H "Content-Type: application/json" \
  "$AEM_SERVER/api/sites.json")

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Success! Sites retrieved:"
  echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
elif [ "$HTTP_CODE" = "401" ]; then
  echo "❌ Authentication Failed! HTTP Status: $HTTP_CODE"
  echo "   Response: $BODY"
elif [ "$HTTP_CODE" = "403" ]; then
  echo "⚠️  Forbidden! HTTP Status: $HTTP_CODE"
  echo "   You don't have permission to list sites."
  echo "   Response: $BODY"
else
  echo "❌ Failed! HTTP Status: $HTTP_CODE"
  echo "   Response: $BODY"
fi
echo ""

# Test 3: GraphQL endpoint (for Quick Site Creation)
echo "Test 3: GraphQL Endpoint (Quick Site Creation)"
echo "-----------------------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  -X POST \
  -H "Authorization: Bearer $AEM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ sites { items { title path } } }"}' \
  "$AEM_SERVER/content/graphql/global/endpoint.json")

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Success! GraphQL endpoint accessible"
  echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
elif [ "$HTTP_CODE" = "401" ]; then
  echo "❌ Authentication Failed! HTTP Status: $HTTP_CODE"
elif [ "$HTTP_CODE" = "404" ]; then
  echo "⚠️  GraphQL endpoint not found (this may be normal)"
else
  echo "❌ Failed! HTTP Status: $HTTP_CODE"
  echo "   Response: $BODY"
fi
echo ""

# Summary
echo "================================"
echo "Summary"
echo "================================"
if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Your AEM credentials are working!"
  echo "   You should be able to use MCP tools successfully."
else
  echo "❌ There are issues with your AEM connectivity."
  echo ""
  echo "Troubleshooting:"
  echo "1. Check if your AEM token has expired (tokens expire after 24 hours)"
  echo "2. Verify AEM_SERVER URL is correct: $AEM_SERVER"
  echo "3. Generate a new token from Adobe Developer Console"
  echo "4. Ensure your token has permissions for AEM Sites operations"
fi
echo ""
