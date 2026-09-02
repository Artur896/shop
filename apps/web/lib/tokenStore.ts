const ACCESS_KEY = "shopping.access_token";
const REFRESH_KEY = "shopping.refresh_token";

/**
 * Plain localStorage for now (readable by any script on the page). Swapping this for
 * an httpOnly-cookie session, issued by the backend, is the recommended hardening
 * before a real production launch — nothing else in the app needs to change to do
 * that, since every call goes through getAccessToken()/setTokens() here.
 */
export const tokenStore = {
  getAccessToken(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(ACCESS_KEY);
  },
  getRefreshToken(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(REFRESH_KEY);
  },
  setTokens(access: string, refresh?: string) {
    window.localStorage.setItem(ACCESS_KEY, access);
    if (refresh) window.localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear() {
    window.localStorage.removeItem(ACCESS_KEY);
    window.localStorage.removeItem(REFRESH_KEY);
  },
};
