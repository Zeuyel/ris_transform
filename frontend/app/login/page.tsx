import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import LoginForm from '@/components/auth/LoginForm';
import { AUTH_COOKIE } from '@/lib/auth';

type LoginPageProps = {
  searchParams?: Promise<{ next?: string }>;
};

export default async function LoginPage({ searchParams }: LoginPageProps) {
  const cookieStore = await cookies();
  const existing = cookieStore.get(AUTH_COOKIE);
  if (existing?.value === '1') {
    redirect('/');
  }

  const resolved = searchParams ? await searchParams : undefined;
  const nextPath = typeof resolved?.next === 'string' ? resolved.next : '/';
  return <LoginForm nextPath={nextPath} />;
}
