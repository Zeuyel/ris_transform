import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';
import { AUTH_COOKIE } from '@/lib/auth';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const localePrefix = '/zh-CN';
  const hasLocalePrefix =
    pathname === localePrefix || pathname.startsWith(`${localePrefix}/`);
  const normalizedPath = hasLocalePrefix
    ? pathname.slice(localePrefix.length) || '/'
    : pathname;

  const password = process.env.FRONTEND_PASSWORD;
  if (!password) {
    if (!hasLocalePrefix) {
      return NextResponse.next();
    }
    const rewriteUrl = request.nextUrl.clone();
    rewriteUrl.pathname = normalizedPath;
    return NextResponse.rewrite(rewriteUrl);
  }

  if (normalizedPath.startsWith('/_next') || normalizedPath === '/favicon.ico') {
    return NextResponse.next();
  }

  if (
    normalizedPath.startsWith('/login') ||
    normalizedPath.startsWith('/api/login')
  ) {
    if (!hasLocalePrefix) {
      return NextResponse.next();
    }
    const rewriteUrl = request.nextUrl.clone();
    rewriteUrl.pathname = normalizedPath;
    return NextResponse.rewrite(rewriteUrl);
  }

  const cookie = request.cookies.get(AUTH_COOKIE);
  if (cookie?.value === '1') {
    if (!hasLocalePrefix) {
      return NextResponse.next();
    }
    const rewriteUrl = request.nextUrl.clone();
    rewriteUrl.pathname = normalizedPath;
    return NextResponse.rewrite(rewriteUrl);
  }

  const loginUrl = request.nextUrl.clone();
  loginUrl.pathname = hasLocalePrefix ? `${localePrefix}/login` : '/login';
  loginUrl.searchParams.set('next', normalizedPath);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
