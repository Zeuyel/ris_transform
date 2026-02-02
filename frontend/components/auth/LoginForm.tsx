'use client';

import { useState } from 'react';

type LoginFormProps = {
  nextPath: string;
};

export default function LoginForm({ nextPath }: LoginFormProps) {
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      });

      if (!response.ok) {
        setError('密码错误');
        return;
      }

      const target = nextPath && nextPath.startsWith('/') ? nextPath : '/';
      window.location.href = target;
    } catch {
      setError('登录失败，请稍后重试');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <main className="mx-auto flex min-h-screen max-w-md items-center px-4">
        <form
          onSubmit={onSubmit}
          className="w-full rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <h1 className="text-xl font-semibold text-slate-900">登录</h1>
          <p className="mt-1 text-sm text-slate-500">请输入访问密码</p>

          <label className="mt-6 block text-sm font-medium text-slate-700">
            密码
            <input
              type="password"
              className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoFocus
              required
            />
          </label>

          {error ? (
            <p className="mt-3 text-sm text-rose-600">{error}</p>
          ) : null}

          <button
            type="submit"
            className="mt-6 w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
            disabled={submitting}
          >
            {submitting ? '登录中...' : '登录'}
          </button>
        </form>
      </main>
    </div>
  );
}
