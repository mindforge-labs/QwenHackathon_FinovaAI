import { PropsWithChildren, ReactNode } from "react";

import { cn } from "@/lib/utils";

import { eyebrow as eyebrowText, sectionCard } from "./ui";

export function SectionCard({
  id,
  eyebrow,
  title,
  subtitle,
  actions,
  className,
  children,
}: PropsWithChildren<{
  id?: string;
  eyebrow?: string;
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  className?: string;
}>) {
  return (
    <section className={cn(sectionCard, className)} id={id}>
      <header className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          {eyebrow ? <p className={eyebrowText}>{eyebrow}</p> : null}
          <h2 className="mt-2 [font-family:'Arial_Black',Impact,Inter,sans-serif] text-[clamp(2rem,3.8vw,3.2rem)] font-black leading-[0.88] tracking-[-0.05em] text-[#0e0f0c]">
            {title}
          </h2>
          {subtitle ? <p className="mt-3 max-w-3xl text-[1.02rem] leading-7 text-[#454745]">{subtitle}</p> : null}
        </div>
        {actions ? <div className="flex flex-wrap items-center gap-3">{actions}</div> : null}
      </header>
      {children}
    </section>
  );
}
