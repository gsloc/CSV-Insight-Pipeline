/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // We rely on TypeScript's own type-checking; skip the separate ESLint pass at
  // build time to keep the production build self-contained.
  eslint: { ignoreDuringBuilds: true },
};

export default nextConfig;
