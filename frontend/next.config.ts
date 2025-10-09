import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  output: 'standalone',
  images: {
    unoptimized: true,
  },
  outputFileTracingRoot: path.join(__dirname), // Adjust path as needed

};

export default nextConfig;
