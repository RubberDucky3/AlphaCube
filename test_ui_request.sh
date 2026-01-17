#!/bin/bash
echo "Testing UI with simple scramble..."
curl -X POST http://127.0.0.1:5000/solve \
  -H "Content-Type: application/json" \
  -d '{"scramble":"R U R'\'' U'\''"}' \
  2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print('Scramble:', data.get('scramble')); print('Cross:', data.get('cross_solution')); print('F2L BL:', data.get('f2l_bl')); print('F2L BR:', data.get('f2l_br')); print('F2L FR:', data.get('f2l_fr')); print('F2L FL:', data.get('f2l_fl')); print('Error:', data.get('error'))"
