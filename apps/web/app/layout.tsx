import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HeatShield | Urban Cooling Intelligence",
  description: "Physics-aware urban heat mitigation and cooling strategy optimization",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
