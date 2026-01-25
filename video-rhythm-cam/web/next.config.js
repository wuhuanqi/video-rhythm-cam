/** @type {import('next').NextConfig} */
const nextConfig = {
  // 启用实验性功能
  experimental: {
    serverActions: {
      bodySizeLimit: '100mb',
    },
  },

  // API 重写到 Python 后端
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },

  // Webpack 配置
  webpack: (config) => {
    // 支持 FFmpeg
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
    };
    return config;
  },

  // 输出配置
  output: 'standalone',

  // 图片优化
  images: {
    domains: ['localhost'],
  },
};

module.exports = nextConfig;
