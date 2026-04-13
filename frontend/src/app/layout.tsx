import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "Finova AI Review Console",
  description: "Loan document intake and review dashboard.",
  icons: {
    icon: "/icon.png",
  }
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">
          <header className="app-header">
            <Link className="brand-mark" href="/applications">
              <span className="brand-mark__eyebrow">Risk intelligence</span>
              <span className="brand-mark__name">Finova AI</span>
            </Link>
            <nav className="app-nav">
              <Link href="/applications">Applications</Link>
            </nav>
            <div className="app-header__actions">
              <span className="signal-pill signal-pill--positive">Live demo mode</span>
            </div>
          </header>
          <main className="app-main">{children}</main>
        </div>
      </body>
    </html>
  );
}
