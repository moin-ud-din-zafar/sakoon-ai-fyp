import { useEffect } from "react";
import { useAuth } from "@clerk/react";

/**
 * When localStorage is cleared, redirect to login without calling Clerk's
 * signOut() (which would 401 when the session token is already gone).
 * Full page redirect so Clerk reinitializes and doesn't get stuck loading.
 */
export default function SignOutOnStorageClear() {
  const { isSignedIn, isLoaded } = useAuth();

  useEffect(() => {
    if (!isLoaded) return;

    const redirectToLogin = () => {
      window.location.replace("/login");
    };

    const hasClerkKeys = () =>
      Object.keys(localStorage).some((k) => k.startsWith("__clerk"));

    const handleStorageChange = (event) => {
      if (event.newValue !== null) return;
      if (!isSignedIn) return;
      const isClerkKey =
        event.key === null || (event.key && event.key.startsWith("__clerk"));
      if (!isClerkKey) return;
      redirectToLogin();
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState !== "visible" || !isSignedIn) return;
      if (!hasClerkKeys()) redirectToLogin();
    };

    // Same-tab clear: storage event doesn't fire, so poll when signed in
    const interval =
      isSignedIn &&
      setInterval(() => {
        if (!hasClerkKeys()) redirectToLogin();
      }, 1000);

    window.addEventListener("storage", handleStorageChange);
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      window.removeEventListener("storage", handleStorageChange);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      if (interval) clearInterval(interval);
    };
  }, [isLoaded, isSignedIn]);

  return null;
}
