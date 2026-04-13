import { PropsWithChildren, ReactNode } from "react";

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
    <section className={["section-card", className].filter(Boolean).join(" ")} id={id}>
      <header className="section-card__header">
        <div>
          {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
          <h2>{title}</h2>
          {subtitle ? <p>{subtitle}</p> : null}
        </div>
        {actions ? <div className="section-card__actions">{actions}</div> : null}
      </header>
      {children}
    </section>
  );
}
