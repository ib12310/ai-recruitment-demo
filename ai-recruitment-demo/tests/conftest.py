import os

# Set a dummy API key before the app is imported so the Anthropic client
# can be instantiated without a real key. Actual calls are mocked in tests.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-api-key")
