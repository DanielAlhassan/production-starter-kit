🏛️ THE ELITE MASTER PRD (v2.0)

Project Standard: 2026 Production-Grade AI-Native Applications

1. THE GOLDEN TECH STACK

Frontend: Next.js 15+ (App Router), TypeScript (Strict Mode).

Backend/Auth/DB: Supabase (PostgreSQL, Auth, Edge Functions, Storage).

Validation: Zod (Mandatory for all data schemas and form inputs).

Data Fetching: TanStack Query v5 (for caching, loading states, and refetching).

UI & Styling: Tailwind CSS + Shadcn UI + Framer Motion (for premium feel).

Infrastructure: Vercel (Hosting), Resend (Email), Sentry (Monitoring).

2. ARCHITECTURAL MANDATES (The Rules)

A. Data & Security

Strict RLS: Every table in Supabase must have Row Level Security. Data must be scoped to auth.uid().

Server Actions: All database writes must use Next.js Server Actions with Zod validation.

Environment Variables: No hardcoded keys. All secrets must be in .env.local.

B. User Experience (UX)

Zero Flicker: Use loading.tsx skeletons for all data-heavy pages.

Optimistic UI: Updates (like "responding to a review") must show in the UI immediately while the server processes.

Tactile Feedback: Use sonner for toast notifications and Framer Motion for button interactions (scale-down on click).

Mobile First: All layouts must be fully responsive for busy business owners on the go.

C. Code Quality

No 'any' types: TypeScript interfaces must be used for all objects.

Modular Components: Shared UI stays in /components/ui, feature logic in /components/features.

Error Handling: Every async operation must be wrapped in a try/catch with user-friendly error messages.

3. PRODUCTION CHECKLIST

[ ] Zod schema for every form/API input.

[ ] Loading skeletons for every route.

[ ] Error boundaries for critical components.

[ ] Mobile-responsive layout verification.

[ ] RLS policies verified in Supabase.
