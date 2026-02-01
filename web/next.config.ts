import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: [
    "http://192.168.1.72",
    "http://192.168.1.72:3000",
    "http://192.168.1.72:3001",
  ],
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "127.0.0.1",
        port: "8000",
        pathname: "/media/**",
      },
      {
        protocol: "http",
        hostname: "192.168.1.72",
        port: "8000",
        pathname: "/media/**",
      },
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/media/**",
      },
    ],
  },
};

export default nextConfig;
