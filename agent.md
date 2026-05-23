# Sakoon AI FYP Repository Guide

This file is a fast map of the codebase. Read it first if you need to understand the app flow, where features live, and which parts are still mock or placeholder UI.

## 1. What This App Is

Sakoon AI is a React + Vite frontend for a mental-wellness / therapy-style experience. The current implementation is primarily a client-side UI with Clerk authentication, protected routes, and a session dashboard built from static or dummy data.

Main technologies:

- React 19
- Vite
- React Router DOM
- Clerk for authentication
- Tailwind CSS utility classes
- Font Awesome icons

## 2. Startup Flow

App startup begins in [src/main.jsx](src/main.jsx). That file:

- Loads the global stylesheet from [src/index.css](src/index.css)
- Configures Font Awesome to avoid duplicate CSS injection
- Reads `VITE_CLERK_PUBLISHABLE_KEY` from the environment
- Wraps the app in `ClerkProvider`
- Mounts [src/App.jsx](src/App.jsx)

If `VITE_CLERK_PUBLISHABLE_KEY` is missing, the app throws immediately. The repo expects a `.env` file at the root with that key.

## 3. Routing And Screen Flow

The top-level router lives in [src/App.jsx](src/App.jsx). The app uses a guarded route model:

- Public routes: `/login`, `/register`, `/forgot-password`
- Protected routes: `/`, `/session`, `/home`, `/chat`, `/summary`, `/mood-tracker`, `/psycho-education`, `/settings`
- Fallback: unknown routes redirect to `/session`

Route behavior:

- `/` immediately redirects to `/session` if the user is authenticated
- `/session` is the main landing area after sign-in
- `/home` currently renders the same session page as `/session`
- `/chat` opens the text-chat view tied to the session UI
- `/summary` displays a grid of feature cards showcasing Sakoon AI benefits
- The remaining protected routes are present but still simple placeholder pages

## 4. Authentication Flow

Authentication is entirely handled by Clerk on the frontend.

### Login and register

The auth screens are in [src/pages/auth/Login.jsx](src/pages/auth/Login.jsx) and [src/pages/auth/Register.jsx](src/pages/auth/Register.jsx).

- Both pages render Clerk components (`SignIn` / `SignUp`)
- Both pages use a responsive two-panel layout with a large image panel on larger screens
- Login redirects into `/session`
- Register redirects into `/session`
- Login includes a link to forgot-password recovery

### Forgot password

[src/pages/auth/ForgotPassword.jsx](src/pages/auth/ForgotPassword.jsx) uses Clerk’s password reset flow:

- User enters email
- App sends a reset code
- User verifies the code
- User submits a new password
- On success, the app navigates back to `/session`

### Route protection

[src/components/auth/ProtectedRoute.jsx](src/components/auth/ProtectedRoute.jsx) checks Clerk auth state:

- While Clerk is loading, it shows a loading message
- If the user is not signed in, it redirects to `/login`
- If signed in, it renders the route content

### Storage-clear handling

[src/components/auth/SignOutOnStorageClear.jsx](src/components/auth/SignOutOnStorageClear.jsx) is a defensive helper for Clerk session state:

- If localStorage loses Clerk session keys, it redirects to `/login`
- It handles same-tab clears with polling because the browser storage event does not fire there
- This prevents the app from getting stuck with a broken Clerk session

## 5. Main App Shell

[src/components/layout/Header.jsx](src/components/layout/Header.jsx) is the primary global shell element.

Key features:

- **Sticky positioning**: The header stays at the top as content scrolls (uses `sticky top-0 z-50`)
- Desktop navigation links for the protected feature pages
- Mobile menu behavior for smaller screens
- Signed-in actions through Clerk’s `Show` and `UserButton`
- Signed-out links to login and register

### Mobile behavior

On mobile screens:
- The Clerk `UserButton` appears in the main header bar (before the hamburger icon) for quick access to the profile
- The hamburger icon animates smoothly to an X sign when the menu opens
- A gap (`ml-3`) separates the profile icon from the hamburger button
- The mobile menu dropdown contains navigation links and session action buttons, but excludes the profile icon
- The mobile menu is controlled by a custom `@media (max-width: 1480px)` rule in [src/index.css](src/index.css), not the default Tailwind breakpoint
- The menu automatically closes again when the viewport grows past 1480px so it does not stay open on large screens after responsive testing

The navigation currently points to:

- Session
- Summary
- Mood Tracker
- Psycho Education
- Settings

The `End Session`, `Save Session`, and `Share` controls are present in the header UI, but they currently behave as interface controls rather than wired backend actions.

## 6. Session Experience

The core product experience is in the session components under [src/components/session](src/components/session).

### Session page composition

[src/components/session/SessionPage.jsx](src/components/session/SessionPage.jsx) is the main dashboard layout for `/session`.

It combines:

- [VideoSessionPanel.jsx](src/components/session/VideoSessionPanel.jsx)
- [LiveTranscript.jsx](src/components/session/LiveTranscript.jsx)
- [EmotionStatePanel.jsx](src/components/session/EmotionStatePanel.jsx)
- [SessionNotesPanel.jsx](src/components/session/SessionNotesPanel.jsx)

### Video panel

[src/components/session/VideoSessionPanel.jsx](src/components/session/VideoSessionPanel.jsx) renders a session-style hero card.

It currently:

- Shows a dummy avatar image
- Displays a live-updating clock
- Provides microphone and speaker toggle buttons
- Includes a large push-to-talk style mic button

This is UI behavior only. There is no real media stream or WebRTC integration yet.

### Live transcript

[src/components/session/LiveTranscript.jsx](src/components/session/LiveTranscript.jsx) renders transcript items from static dummy data.

It currently:

- Reads messages from `LIVE_TRANSCRIPT_DUMMY`
- Shows speaker labels, timestamps, and message content
- Includes session action buttons below the transcript area
- Links to `/chat` through a chat icon

### Emotional state panel

[src/components/session/EmotionStatePanel.jsx](src/components/session/EmotionStatePanel.jsx) visualizes a mood snapshot.

It uses dummy data for:

- Current state label
- Valence slider
- Arousal slider
- Confidence percentage

The emoji mapping also comes from the constants file.

### Session notes panel

[src/components/session/SessionNotesPanel.jsx](src/components/session/SessionNotesPanel.jsx) shows a bullet list of discussion topics.

The notes are sourced from static dummy data and are not yet editable.

### Chat panel

[src/components/session/ChatPanel.jsx](src/components/session/ChatPanel.jsx) is the text-chat version of the session experience.

It currently:

- Renders the same dummy transcript data
- Has a message input with Enter-to-send behavior
- Clears the input on send, but does not call an API or store messages
- Repeats the session action buttons below the chat area

## 7. Other Pages

### Summary page

[src/pages/Summary/Summary.jsx](src/pages/Summary/Summary.jsx) displays a feature grid showcasing Sakoon AI's key offerings.

It includes:
- A page heading ("Why Choose Sakoon AI?") and subtitle
- A responsive 3-column grid (1 col on mobile, 2 on tablet, 3 on desktop)
- Feature cards mapped from a `FEATURES` array
- Each card displays an icon, title, and description using the `FeatureCard` component

Current features:
- Voice-First Therapy
- Multilingual Support
- Privacy & Security
- 24/7 Availability
- Personalized Care
- Human Backup

### Placeholder pages

These routes exist but currently render a centered title:

- [src/pages/MoodTracker/MoodTracker.jsx](src/pages/MoodTracker/MoodTracker.jsx)
- [src/pages/PsychoEducation/PsychoEducation.jsx](src/pages/PsychoEducation/PsychoEducation.jsx)
- [src/pages/Settings/Settings.jsx](src/pages/Settings/Settings.jsx)

Each is ready for future expansion.

## 8. Shared Data And UI Helpers

### Dummy constants

[src/constants/constantdummydata.js](src/constants/constantdummydata.js) stores all static content used by the session UI:

- `EMOTIONAL_STATE_EMOJI`
- `EMOTIONAL_STATE_DUMMY`
- `LIVE_TRANSCRIPT_DUMMY`
- `notes`

This file is the main mock data source for the current dashboard.

### Feature card component

[src/components/common/FeatureCard.jsx](src/components/common/FeatureCard.jsx) is a reusable card component used by the Summary page.

It displays:
- An icon in a circular badge at the top
- Title and description text below (left-aligned)
- Accepts `icon` (Font Awesome icon object), `title` (string), and `description` (string) props

### Reusable button

[src/components/common/Button.jsx](src/components/common/Button.jsx) is a small shared button primitive.

It supports:

- Text labels
- Optional icon rendering
- Border vs no-border styling
- A small set of color presets

## 9. Styling Notes

Global styling is in [src/index.css](src/index.css).

Important details:

- Tailwind is imported globally
- The app uses a light neutral theme by default
- `html`, `body`, and `#root` are forced to full height
- `#root` now spans the full width of the viewport so the header and main shell can stretch edge to edge
- The session notes list has custom marker color styling
- The old Vite starter styles from [src/App.css](src/App.css) were folded into [src/index.css](src/index.css) and the file was removed
- The responsive header visibility rules also live in [src/index.css](src/index.css)

## 10. File-Level Mental Model

Use this when deciding where new code should go:

- App bootstrap and providers: [src/main.jsx](src/main.jsx)
- Route definitions and top-level guards: [src/App.jsx](src/App.jsx)
- Auth/session route enforcement: [src/components/auth/ProtectedRoute.jsx](src/components/auth/ProtectedRoute.jsx)
- Session cleanup fallback logic: [src/components/auth/SignOutOnStorageClear.jsx](src/components/auth/SignOutOnStorageClear.jsx)
- Global sticky nav and action shell: [src/components/layout/Header.jsx](src/components/layout/Header.jsx)
- Main session dashboard: [src/components/session/SessionPage.jsx](src/components/session/SessionPage.jsx)
- Text chat page: [src/pages/ChatPage/Chat.jsx](src/pages/ChatPage/Chat.jsx)
- Summary page with features grid: [src/pages/Summary/Summary.jsx](src/pages/Summary/Summary.jsx)
- Mock data: [src/constants/constantdummydata.js](src/constants/constantdummydata.js)
- Reusable components: [src/components/common/](src/components/common/) (Button, FeatureCard)

## 11. Current State And Gaps

The app is structurally complete as a frontend shell, but several flows are still mock or incomplete:

- Session controls are not wired to real backend actions
- Transcript, notes, and emotional state are static dummy content
- Mood tracking, psycho-education, and settings are still placeholder pages
- Summary page is now populated with a features grid (ready for customization)
- There is no backend API layer in this repo yet
- Clerk is the only real external integration currently wired into the app
- The header is responsive at a custom 1480px breakpoint and includes a resize-safe mobile menu
- There is no separate App.css or Header.css file anymore; those styles were consolidated into [src/index.css](src/index.css)

## 12. Practical Editing Rule

If you need to change something, first decide whether it belongs to:

- routing / auth flow
- global shell / navigation (sticky header, hamburger menu animation, mobile responsiveness)
- session UI composition
- page content (Summary features grid, placeholder pages)
- dummy data constants
- shared button or card components

That separation will keep changes small and avoid mixing mock UI with future production logic.