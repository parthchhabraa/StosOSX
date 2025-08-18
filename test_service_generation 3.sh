#!/bin/bash

# Test service file generation with dynamic user

echo "Testing StosOS service file generation..."

# Configuration
STOSOS_USER="$USER"
STOSOS_HOME="$HOME"
STOSOS_DIR="$STOSOS_HOME/stosos"

echo "User: $STOSOS_USER"
echo "Home: $STOSOS_HOME"
echo "StosOS Dir: $STOSOS_DIR"
echo "UID: $(id -u)"

# Create test directory
TEST_DIR="/tmp/stosos_service_test"
mkdir -p "$TEST_DIR"

# Copy service file and apply transformations
cp stosos.service "$TEST_DIR/stosos.service"

# Apply the same transformations as install script
sed -i "s|STOSOS_USER_PLACEHOLDER|$STOSOS_USER|g" "$TEST_DIR/stosos.service"
sed -i "s|STOSOS_DIR_PLACEHOLDER|$STOSOS_DIR|g" "$TEST_DIR/stosos.service"
sed -i "s|UID_PLACEHOLDER|$(id -u)|g" "$TEST_DIR/stosos.service"

echo ""
echo "Generated service file:"
echo "======================="
cat "$TEST_DIR/stosos.service"

# Cleanup
rm -rf "$TEST_DIR"

echo ""
echo "✅ Service file generation test completed!"