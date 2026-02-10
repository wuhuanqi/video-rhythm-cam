import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PIPI Audio Sync - 智能音频对齐",
  description: "用高质量音频替换你的舞蹈视频，AI 自动对齐卡点",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN" className="dark">
      <body className="font-display">
        {children}
      </body>
    </html>
  );
}
