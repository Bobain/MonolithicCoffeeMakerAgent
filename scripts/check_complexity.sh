#!/bin/bash
# Check code complexity metrics

echo "=== Code Complexity Report ==="
echo ""

echo "Cyclomatic Complexity (should be <10 per function):"
radon cc coffee_maker/ -a -s

echo ""
echo "Maintainability Index (should be >20):"
radon mi coffee_maker/ -s

echo ""
echo "Pylint Score (should be >8.0):"
pylint coffee_maker/ --score=y || true
