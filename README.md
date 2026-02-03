# Flow V0

Flow is a quiet writing environment with inline AI suggestions and word-level annotations.

## Setup

```bash
npm install
```

Create a `.env.local` file with:

```bash
GEMINI_API_KEY=your_key_here
```

Run the app:

```bash
npm run dev
```

## Notes

- Suggestions come from `/api/suggest` using the Gemini REST API.
- Draft text and annotations are stored in localStorage.
