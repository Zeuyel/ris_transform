/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  async rewrites() {
    const backendURL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${backendURL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;

