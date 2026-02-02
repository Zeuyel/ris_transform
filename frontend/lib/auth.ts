export const AUTH_COOKIE = 'ris_auth';

export function isAuthEnabled(): boolean {
  return Boolean(process.env.FRONTEND_PASSWORD);
}
