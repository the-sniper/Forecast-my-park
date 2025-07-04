import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geist = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Forecast My Park - AI-Powered Park Visitor Predictions",
  description: "Get accurate visitor forecasts for US National Parks using advanced machine learning. Plan your visit or manage park operations with confidence.",
  keywords: ["national parks", "visitor forecast", "AI predictions", "machine learning", "tourism planning"],
  authors: [{ name: "Forecast My Park Team" }],
  openGraph: {
    title: "Forecast My Park - AI-Powered Park Visitor Predictions",
    description: "Get accurate visitor forecasts for US National Parks using advanced machine learning.",
    type: "website",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geist.variable} ${geistMono.variable} antialiased`}>
        {children}
      </body>
    </html>
  );
}
