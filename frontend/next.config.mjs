/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  async rewrites() {
    const backendURL =
      process.env.NEXT_PUBLIC_API_URL ||
      (process.env.NODE_ENV === 'production'
        ? 'http://backend:8000'
        : 'http://127.0.0.1:8000');
    return [
      {
        source: '/api/:path*',
        destination: `${backendURL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;

