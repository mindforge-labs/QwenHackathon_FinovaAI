import type { Metadata } from "next";
import Link from "next/link";

import { appShell, displayFont, pageContainer, pageGrid, signalPillStyles } from "@/components/common/ui";

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
      <body
        className="min-h-screen overflow-x-hidden bg-[radial-gradient(circle_at_top_left,rgba(159,232,112,0.22),transparent_24%),radial-gradient(circle_at_bottom_right,rgba(255,209,26,0.18),transparent_20%),linear-gradient(180deg,#fbfcf7_0%,#eef4e7_100%)] text-[#0e0f0c] antialiased [font-family:Inter,'Helvetica_Neue',Arial,sans-serif]"
        style={{ fontFeatureSettings: '"calt" 1' }}
      >
        <div className={appShell}>
          <header className={`${pageContainer} grid gap-5 py-[26px] pb-[18px] md:grid-cols-[auto_1fr_auto] md:items-center md:gap-6`}>
            <Link className="grid gap-0.5 no-underline" href="/applications">
              <span className="text-[0.72rem] font-bold uppercase tracking-[0.14em] text-[#6c7268]">
                Risk intelligence
              </span>
              <span className={`${displayFont} text-[1.72rem] leading-[0.92] text-[#0e0f0c]`}>
                Finova AI
              </span>
            </Link>
            <nav className="flex flex-wrap justify-center gap-3">
              <Link
                className="rounded-full px-4 py-2.5 text-sm font-semibold text-[#454745] transition duration-200 hover:-translate-y-0.5 hover:bg-[#d3f2c0]/70"
                href="/applications"
              >
                Applications
              </Link>
            </nav>
            <div className="flex justify-start md:justify-end">
              <span className={signalPillStyles("positive")}>Live demo mode</span>
            </div>
          </header>
          <main className={`${pageContainer} ${pageGrid}`}>{children}</main>
        </div>
      </body>
    </html>
  );
}
