# Lets Learn Frontend

Beautiful Next.js frontend powered by shadcn/ui. It fetches lessons from the local API at
`http://127.0.0.1:8000/api/lets-learn/` and renders a modern, card-based dashboard.

## Getting Started

1. Make sure your backend API is running at `http://127.0.0.1:8000`.
2. Start the development server:

```
npm run dev
```

3. Open `http://localhost:3000` in your browser.

## Project Notes

- UI is built with shadcn/ui components.
- Data fetching is handled in `app/page.tsx`.
- Loading and error states are defined in `app/loading.tsx` and `app/error.tsx`.
