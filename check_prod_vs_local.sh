#!/bin/bash

echo "=== Production vs Local Environment Comparison ==="
echo

echo "1. Docker version comparison:"
echo "Production:"
ssh your_server "docker --version"
echo "Local:"
docker --version
echo

echo "2. Python version in production:"
ssh your_server "docker exec django_fitrat python --version"
echo "Local (expected): Python 3.13.0"
echo

echo "3. Check if production has build tools:"
ssh your_server "docker exec django_fitrat apk list | grep -E '(gcc|build-base|make)' | head -5"
echo

echo "4. Check problematic packages in production:"
ssh your_server "docker exec django_fitrat pip show grpcio cryptography cffi | grep -E '(Name|Version|Location)'"
echo

echo "5. Check package installation method in production:"
ssh your_server "docker exec django_fitrat pip show grpcio | grep -A 5 'Location'"
echo

echo "6. Check if production uses different base image:"
ssh your_server "docker exec django_fitrat cat /etc/os-release"
echo

echo "7. Check production container build history:"
ssh your_server "docker history django_fitrat --no-trunc | head -10"
echo

echo "=== Commands to run on production server ==="
echo "Run these commands directly on your production server:"
echo
echo "docker exec django_fitrat python --version"
echo "docker exec django_fitrat pip show grpcio"
echo "docker exec django_fitrat apk list | grep -E '(gcc|build|make)'"
echo "docker exec django_fitrat cat /etc/os-release"
echo "docker history django_fitrat --no-trunc | head -5"
