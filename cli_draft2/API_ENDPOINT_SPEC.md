# API Endpoint Specification: `/api/submissions`

## Overview
Create a Next.js API route at `/api/submissions` that handles fetching submissions from Supabase.

## Endpoint Details

**Path:** `/api/submissions`  
**Method:** `GET`  
**Location:** `pages/api/submissions.ts` (Pages Router) or `app/api/submissions/route.ts` (App Router)

## Query Parameters

- `limit` (optional, default: 10) - Maximum number of submissions to return
- `mine` (optional, default: false) - If `"true"`, return only the authenticated user's submissions

## Authentication

- **For `mine=true`**: Requires `Authorization: Bearer <token>` header with valid JWT token
- **For `mine=false` or not provided**: Can be public (no auth required) or use auth if available

## Request Examples

```
GET /api/submissions?limit=10
GET /api/submissions?limit=20&mine=true
```

## Response Format

**Success (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "created_at": "2025-11-20T20:44:18Z",
      "user_id": "uuid",
      "problem_id": "uuid",
      "code": "text",
      "language": "python",
      "metrics": {...},
      "status": "accepted"
    },
    ...
  ]
}
```

**Error (401):**
```json
{
  "error": "Unauthorized"
}
```

**Error (500):**
```json
{
  "error": "Internal server error"
}
```

## Implementation Requirements

### 1. Database Query Logic

- Query the `public.submissions` table in Supabase
- If `mine=true`:
  - Extract `user_id` from JWT token
  - Filter: `WHERE user_id = <extracted_user_id>`
- Order by: `created_at DESC`
- Limit: Use `limit` parameter (default 10)

### 2. Authentication Handling

- Extract JWT token from `Authorization` header
- Verify token with Supabase Auth (if using Supabase client)
- Extract `user_id` from token payload (field: `sub`)

### 3. Supabase Query Example (using Supabase JS client)

```typescript
import { createClient } from '@supabase/supabase-js'

// For mine=true
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
const { data: { user } } = await supabase.auth.getUser(token)

const { data, error } = await supabase
  .from('submissions')
  .select('*')
  .eq('user_id', user.id)
  .order('created_at', { ascending: false })
  .limit(limit)

// For public (mine=false)
const { data, error } = await supabase
  .from('submissions')
  .select('*')
  .order('created_at', { ascending: false })
  .limit(limit)
```

### 4. Error Handling

- 401: If `mine=true` but no valid token provided
- 500: Database errors, invalid queries, etc.
- Return appropriate error messages

### 5. CORS (if needed)

If calling from CLI, ensure CORS headers are set:
```typescript
res.setHeader('Access-Control-Allow-Origin', '*')
res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
res.setHeader('Access-Control-Allow-Headers', 'Authorization, Content-Type')
```

## Example Implementation (Pages Router)

```typescript
// pages/api/submissions.ts
import type { NextApiRequest, NextApiResponse } from 'next'
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const { limit = 10, mine = false } = req.query
  const limitNum = parseInt(limit as string, 10)
  const isMine = mine === 'true'

  const supabase = createClient(supabaseUrl, supabaseAnonKey)

  try {
    // If mine=true, require authentication
    if (isMine) {
      const authHeader = req.headers.authorization
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({ error: 'Unauthorized' })
      }

      const token = authHeader.replace('Bearer ', '')
      const { data: { user }, error: authError } = await supabase.auth.getUser(token)
      
      if (authError || !user) {
        return res.status(401).json({ error: 'Invalid token' })
      }

      // Query user's submissions
      const { data, error } = await supabase
        .from('submissions')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(limitNum)

      if (error) {
        console.error('Supabase error:', error)
        return res.status(500).json({ error: 'Database error' })
      }

      return res.status(200).json({ data: data || [] })
    } else {
      // Public query - all submissions
      const { data, error } = await supabase
        .from('submissions')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(limitNum)

      if (error) {
        console.error('Supabase error:', error)
        return res.status(500).json({ error: 'Database error' })
      }

      return res.status(200).json({ data: data || [] })
    }
  } catch (error) {
    console.error('API error:', error)
    return res.status(500).json({ error: 'Internal server error' })
  }
}
```

## Testing

Test with:
```bash
# Public submissions
curl https://tinytorch.netlify.app/api/submissions?limit=10

# User's submissions (requires token)
curl -H "Authorization: Bearer <token>" \
  https://tinytorch.netlify.app/api/submissions?limit=10&mine=true
```

## Notes

- The CLI expects the response in `{"data": [...]}` format
- Ensure RLS (Row Level Security) policies on Supabase allow:
  - Public read access for `mine=false`
  - User-specific read access for `mine=true` (filtered by user_id)
- The endpoint should match the pattern of your existing `/api/leaderboard` endpoint
