## Configuration File Location

**File:** `src/config/apiConfig.ts`

This file reads from environment variables with fallback to localhost defaults.

## Environment Variables

Create a `.env` file in the **project root** (same level as `package.json`) with:

```env
VITE_COESI_API_BASE=http://server
VITE_LEGACY_API_BASE=http://server:8000
VITE_YAML_BUILDER_URL=http://server:8099
```

## Important Notes

1. **Environment variables MUST start with `VITE_`** for Vite to expose them
2. After changing `.env`, you **MUST restart the development server** or rebuild
3. The `.env` file should be in the **project root**, not in `src/`

