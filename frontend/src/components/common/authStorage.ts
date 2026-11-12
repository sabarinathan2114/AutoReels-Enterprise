export interface AuthUserData {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  workspace_id?: string;
  plan_id?: string;
}

const TOKEN_KEY = "az_jwt_token";
const USER_KEY = "az_user";

export const AuthStorage = {
  saveSession(token: string, user: AuthUserData): void {
    if (typeof window !== "undefined") {
      sessionStorage.setItem(TOKEN_KEY, token);
      sessionStorage.setItem(USER_KEY, JSON.stringify(user));
    }
  },

  getToken(): string | null {
    if (typeof window !== "undefined") {
      return sessionStorage.getItem(TOKEN_KEY);
    }
    return null;
  },

  getUser(): AuthUserData | null {
    if (typeof window !== "undefined") {
      const data = sessionStorage.getItem(USER_KEY);
      if (data) {
        try {
          return JSON.parse(data);
        } catch {
          return null;
        }
      }
    }
    return null;
  },

  clearSession(): void {
    if (typeof window !== "undefined") {
      sessionStorage.removeItem(TOKEN_KEY);
      sessionStorage.removeItem(USER_KEY);
    }
  },

  isAuthenticated(): boolean {
    return Boolean(this.getToken());
  }
};
