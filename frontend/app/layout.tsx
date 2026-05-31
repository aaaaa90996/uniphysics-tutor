import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'UniPhysics Tutor - 本科物理数字人智能助教',
  description: '面向本科生的物理数字人智能助教，支持概念讲解、分步解题、误区诊断和练习生成',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <head>
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css"
          integrity="sha384-n8MVd4RsNHUKE2T0PhDPzhGQxImB3IozK7M6mHhOTwNhZEdhPMZHcMnmkpxMAxI"
          crossOrigin="anonymous"
        />
      </head>
      <body className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
        {children}
      </body>
    </html>
  );
}
