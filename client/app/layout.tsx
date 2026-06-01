import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CSV Insight Pipeline",
  description: "Ingest, validate, clean, and analyze CSV files with automated insights.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
