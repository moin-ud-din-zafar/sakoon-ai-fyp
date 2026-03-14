# Clerk + Google Sign-In Setup

This app uses **Clerk** for authentication with **Google** as a sign-in option.

## 1. Environment variable

In your `.env` file (already added):

```
VITE_CLERK_PUBLISHABLE_KEY=pk_test_xxxx
```

Get your **Publishable key** from [Clerk Dashboard](https://dashboard.clerk.com) → API Keys.

## 2. Enable Google in Clerk (required for "Sign in with Google")

**Do not put Google Client Secret in your code or repo.** Configure it only in Clerk:

1. Open [Clerk Dashboard](https://dashboard.clerk.com) → your application.
2. Go to **Configure** → **User & Authentication** → **Social connections**.
3. Enable **Google**.
4. In **Google Cloud Console** ([console.cloud.google.com](https://console.cloud.google.com)):
   - Create or select a project.
   - **APIs & Services** → **Credentials** → **Create credentials** → **OAuth client ID**.
   - Application type: **Web application**.
   - Under **Authorized redirect URIs**, add the exact redirect URL shown in Clerk (e.g. `https://xxxx.clerk.accounts.dev/v1/oauth_callback`).
5. Copy the **Client ID** and **Client Secret** from Google and paste them into Clerk’s Google provider settings, then save.

After this, "Sign in with Google" will work on your Login and Register pages.
