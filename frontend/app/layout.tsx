import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SkillGraph",
  description: "AI-adaptive onboarding engine for hackathon demos."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

