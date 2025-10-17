#!/bin/bash
# Fix all platform issues

# 1. Find AI generator page route
grep -r "def.*ai.*generator" routes/*.py | grep -v "api" | head -1

# 2. Check AI generator template JavaScript API calls
grep -n "fetch.*api.*generator" templates/ai_generator*.html

# 3. Fix API endpoint in template
sed -i "s|fetch('/api/ai-generator/|fetch('/api/ai-generator/|g" templates/ai_generator_page.html

# 4. Verify OpenAI key is set
echo "OPENAI_API_KEY set: $([ -n "$OPENAI_API_KEY" ] && echo YES || echo NO)"

# 5. Test local generation
python3.11 << 'PYEOF'
import os
os.environ.setdefault('OPENAI_API_KEY', 'test')
from routes.ai_generator_advanced import AI_ENABLED
print(f"AI Enabled: {AI_ENABLED}")
PYEOF

