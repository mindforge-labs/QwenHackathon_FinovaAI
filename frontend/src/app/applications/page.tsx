"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import { MetricCard } from "@/components/common/metric-card";
import { PipelineStrip } from "@/components/common/pipeline-strip";
import { SectionCard } from "@/components/common/section-card";
import { StatusBadge } from "@/components/common/status-badge";
import {
  buttonStyles,
  displayFont,
  emptyState,
  eyebrow,
  feedbackError,
  input,
  inverseEyebrow,
  label,
  sectionCardDark,
  signalPillStyles,
} from "@/components/common/ui";
import { useApplications } from "@/hooks/useApplications";
import { ApplicationSummary } from "@/lib/types";
import { cn, formatDate } from "@/lib/utils";

function getApplicationBucket(application: ApplicationSummary): "flagged" | "processing" | "draft" | "approved" {
  if (application.status === "approved") {
    return "approved";
  }

  if (
    application.status === "under_review" ||
    application.status === "rejected" ||
    application.flagged_document_count > 0
  ) {
    return "flagged";
  }

  if (application.status === "processing") {
    return "processing";
  }

  return "draft";
}

export default function ApplicationsPage() {
  const { items, loading, error, addApplication } = useApplications();
  const [form, setForm] = useState({ applicant_name: "", phone: "", email: "" });
  const [submitting, setSubmitting] = useState(false);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await addApplication(form);
      setForm({ applicant_name: "", phone: "", email: "" });
    } finally {
      setSubmitting(false);
    }
  }

  const orderedItems = [...items].sort((left, right) => Date.parse(right.updated_at) - Date.parse(left.updated_at));
  const totalDocuments = orderedItems.reduce((sum, application) => sum + application.document_count, 0);
  const totalFlaggedDocuments = orderedItems.reduce(
    (sum, application) => sum + application.flagged_document_count,
    0,
  );
  const flaggedApplications = orderedItems.filter((application) => getApplicationBucket(application) === "flagged");
  const approvedApplications = orderedItems.filter((application) => application.status === "approved");
  const processingApplications = orderedItems.filter((application) => application.status === "processing");
  const reviewCandidate = orderedItems
    .filter((application) => application.next_review_document_id)
    .sort(
      (left, right) =>
        Date.parse(right.next_review_document_updated_at || right.updated_at) -
        Date.parse(left.next_review_document_updated_at || left.updated_at),
    )[0];

  const groups = [
    {
      key: "flagged",
      title: "Flagged & under review",
      subtitle: "Cases where AI surfaced a risk, mismatch, or low-confidence extraction.",
      items: orderedItems.filter((application) => getApplicationBucket(application) === "flagged"),
    },
    {
      key: "processing",
      title: "Processing queue",
      subtitle: "Applications with documents currently moving through OCR and extraction.",
      items: orderedItems.filter((application) => getApplicationBucket(application) === "processing"),
    },
    {
      key: "draft",
      title: "Draft intake",
      subtitle: "Fresh cases waiting for uploads or their first processing run.",
      items: orderedItems.filter((application) => getApplicationBucket(application) === "draft"),
    },
    {
      key: "approved",
      title: "Approved cases",
      subtitle: "Applications that already cleared review and are ready for the next lending step.",
      items: orderedItems.filter((application) => getApplicationBucket(application) === "approved"),
    },
  ].filter((group) => group.items.length > 0);

  return (
    <>
      <section>
        <div className="relative isolate flex min-h-[calc(100vh-232px)] flex-col justify-between gap-10 overflow-hidden rounded-[40px] border border-white/10 bg-[radial-gradient(circle_at_16%_18%,rgba(159,232,112,0.24),transparent_28%),radial-gradient(circle_at_82%_18%,rgba(255,209,26,0.18),transparent_24%),radial-gradient(circle_at_82%_82%,rgba(56,189,248,0.16),transparent_28%),linear-gradient(122deg,#09120a_0%,#123416_34%,#0f5a42_72%,#2f1f08_100%)] px-[clamp(28px,4vw,56px)] py-[clamp(28px,4vw,56px)] text-[#f7fcef] shadow-[0_24px_60px_rgba(8,17,10,0.28)] lg:flex-row lg:items-center">
          <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(112deg,rgba(255,255,255,0.1),rgba(255,255,255,0)_32%),linear-gradient(180deg,rgba(255,255,255,0.02),rgba(255,255,255,0))]" />
          <div className="relative z-10 max-w-[42rem]">
            <p className={inverseEyebrow}>AI risk review platform</p>
            <h1 className={`${displayFont} mt-4 max-w-[16ch] text-[clamp(2rem,5vw,4rem)] text-[#f7fcef] [text-shadow:0_12px_32px_rgba(0,0,0,0.18)]`}>
              Make the AI visible. Make the risk obvious. Make the human decision powerful.
            </h1>
            <p className="mt-5 max-w-[76ch] text-[1.08rem] leading-8 text-[#edf4e8]/85">
              Finova turns the intake desk into a live command center: upload files, watch OCR and
              extraction flow, then route risky cases into a decisive human review lane.
            </p>
            <div className="mt-7 flex flex-wrap items-center gap-3">
              <Link className={buttonStyles("primary", "shadow-[0_14px_36px_rgba(159,232,112,0.18)]")} href="#create-application">
                Start new application
              </Link>
              {reviewCandidate?.next_review_document_id ? (
                <Link
                  className={buttonStyles("secondary", "bg-white/[0.12] text-[#f8fbf4] shadow-[inset_0_0_0_1px_rgba(255,255,255,0.12)] hover:bg-white/[0.18]")}
                  href={`/review/${reviewCandidate.next_review_document_id}`}
                >
                  Continue last review
                </Link>
              ) : (
                <Link
                  className={buttonStyles("secondary", "bg-white/[0.12] text-[#f8fbf4] shadow-[inset_0_0_0_1px_rgba(255,255,255,0.12)] hover:bg-white/[0.18]")}
                  href="/applications"
                >
                  Monitor queue
                </Link>
              )}
            </div>
          </div>

          <div className="relative z-10 flex justify-center">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              alt="AI review command center"
              className="h-auto w-full max-w-[min(480px,40vw)] rounded-[32px]"
              src="/Banknote-bro.png"
            />
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          detail={`${totalDocuments} document(s) tracked across the desk`}
          label="Total applications"
          tone="neutral"
          value={String(orderedItems.length)}
        />
        <MetricCard
          detail="Applications with flagged documents or manual review activity"
          label="Under review"
          tone="warning"
          value={String(flaggedApplications.length)}
        />
        <MetricCard
          detail={`${totalFlaggedDocuments} flagged document(s) surfaced`}
          label="Flagged"
          tone="danger"
          value={String(totalFlaggedDocuments)}
        />
        <MetricCard
          detail="Cases already cleared by reviewers"
          label="Approved"
          tone="positive"
          value={String(approvedApplications.length)}
        />
      </section>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.45fr)_minmax(340px,0.9fr)]">
        <SectionCard
          eyebrow="Applications"
          subtitle="Grouped by urgency so the review desk can focus where risk is surfacing."
          title="Portfolio queue"
        >
          {loading ? <p>Loading applications...</p> : null}
          {error ? <p className={feedbackError}>{error}</p> : null}

          <div className="grid gap-6">
            {groups.map((group) => (
              <section className="grid gap-4" key={group.key}>
                <header className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <p className={eyebrow}>{group.title}</p>
                    <h3 className="mt-2 text-[1.6rem] font-semibold tracking-[-0.03em] text-[#0e0f0c]">
                      {group.items.length} case(s)
                    </h3>
                  </div>
                  <p className="max-w-2xl text-sm leading-6 text-[#454745]">{group.subtitle}</p>
                </header>

                <div className="grid gap-4">
                  {group.items.map((application) => {
                    const totalDocsForApp = application.document_count;
                    const processedDocs = application.processed_document_count;
                    const flaggedDocs = application.flagged_document_count;
                    const progress = totalDocsForApp === 0 ? 0 : (processedDocs / totalDocsForApp) * 100;

                    return (
                      <Link
                        className="rounded-[30px] border border-black/10 bg-white/[0.82] p-5 shadow-[0_0_0_1px_rgba(14,15,12,0.04)] transition duration-200 hover:-translate-y-1 hover:border-[#9fe870]/40 hover:shadow-[0_18px_40px_rgba(14,15,12,0.08)]"
                        href={`/applications/${application.id}`}
                        key={application.id}
                      >
                        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                          <div>
                            <h3 className="text-[1.45rem] font-semibold tracking-[-0.03em] text-[#0e0f0c]">
                              {application.applicant_name || "Untitled application"}
                            </h3>
                            <p className="mt-2 text-sm leading-6 text-[#454745]">
                              {application.email || application.phone || "No contact info yet"}
                            </p>
                          </div>
                          <div className="flex flex-wrap items-center gap-3">
                            {flaggedDocs > 0 ? (
                              <span className={signalPillStyles("danger")}>
                                {flaggedDocs} risk signal{flaggedDocs > 1 ? "s" : ""}
                              </span>
                            ) : (
                              <span className={signalPillStyles("neutral")}>Clean scan</span>
                            )}
                            <StatusBadge status={application.status} />
                          </div>
                        </div>

                        <div className="mt-4 flex flex-wrap gap-3 text-[0.92rem] text-[#6c7268]">
                          <span>Created {formatDate(application.created_at)}</span>
                          <span>{totalDocsForApp} document(s)</span>
                          <span>{processedDocs} processed</span>
                        </div>

                        <div className="mt-5 grid gap-2">
                          <div className="flex items-center justify-between gap-4 text-sm">
                            <span className="text-[#454745]">
                              {totalDocsForApp > 0
                                ? `${processedDocs}/${totalDocsForApp} documents processed`
                                : "Awaiting uploads"}
                            </span>
                            <strong className="font-semibold text-[#0e0f0c]">{Math.round(progress)}%</strong>
                          </div>
                          <div className="relative h-2.5 overflow-hidden rounded-full bg-black/[0.08]">
                            <span
                              className={cn(
                                "absolute inset-y-0 left-0 rounded-full",
                                flaggedDocs > 0
                                  ? "bg-[#ffd11a]"
                                  : application.status === "approved"
                                    ? "bg-[#054d28]"
                                    : "bg-[#9fe870]",
                              )}
                              style={{ width: `${progress}%` }}
                            />
                          </div>
                        </div>
                      </Link>
                    );
                  })}
                </div>
              </section>
            ))}

            {!loading && orderedItems.length === 0 ? <p className={emptyState}>No applications yet.</p> : null}
          </div>
        </SectionCard>

        <div className="grid gap-6">
          <SectionCard
            actions={<span className={signalPillStyles("soft")}>{submitting ? "Creating..." : "Ready"}</span>}
            eyebrow="Quick action"
            id="create-application"
            subtitle="Kick off a new lending intake case from the dashboard."
            title="Create application"
          >
            <form className="grid gap-4 md:grid-cols-2" onSubmit={(event) => void handleCreate(event)}>
              <label className={label}>
                Applicant Name
                <input
                  className={input}
                  value={form.applicant_name}
                  onChange={(event) => setForm((current) => ({ ...current, applicant_name: event.target.value }))}
                />
              </label>
              <label className={label}>
                Phone
                <input
                  className={input}
                  value={form.phone}
                  onChange={(event) => setForm((current) => ({ ...current, phone: event.target.value }))}
                />
              </label>
              <label className={`${label} md:col-span-2`}>
                Email
                <input
                  className={input}
                  value={form.email}
                  onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
                />
              </label>
              <div className="md:col-span-2">
                <button className={buttonStyles("primary")} disabled={submitting} type="submit">
                  {submitting ? "Creating..." : "Create Application"}
                </button>
              </div>
            </form>
          </SectionCard>

          <aside className={sectionCardDark}>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className={inverseEyebrow}>Processing pipeline</p>
              <h2 className={`${displayFont} mt-2 text-[clamp(1.55rem,2.6vw,2.1rem)] text-[#ecf3e2]`}>
                Command center flow
              </h2>
            </div>
            <span className={signalPillStyles("positive")}>Live</span>
          </div>
          <div className="mt-6">
            <PipelineStrip
            steps={[
              {
                label: "Upload",
                description: `${totalDocuments} document(s) preserved in raw storage`,
                state: totalDocuments > 0 ? "done" : "pending",
              },
              {
                label: "OCR",
                description:
                  processingApplications.length > 0 ? "OCR is running on active cases" : "Waiting for new files",
                state: processingApplications.length > 0 ? "active" : totalDocuments > 0 ? "done" : "pending",
              },
              {
                label: "AI extraction",
                description:
                  flaggedApplications.length > 0
                    ? "Low-confidence fields surfaced for review"
                    : "Structured payloads ready",
                state: flaggedApplications.length > 0 ? "warning" : totalDocuments > 0 ? "done" : "pending",
              },
              {
                label: "Risk detection",
                description: `${flaggedApplications.length} application(s) currently need analyst attention`,
                state: flaggedApplications.length > 0 ? "warning" : totalDocuments > 0 ? "done" : "pending",
              },
            ]}
          />
          </div>
          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            <div className="rounded-[24px] border border-white/10 bg-white/5 px-4 py-4">
              <span className="text-xs font-bold uppercase tracking-[0.14em] text-[#c7d8bb]">Docs monitored</span>
              <strong className="mt-2 block text-3xl font-black tracking-[-0.04em] text-[#f7fcef]">{totalDocuments}</strong>
            </div>
            <div className="rounded-[24px] border border-white/10 bg-white/5 px-4 py-4">
              <span className="text-xs font-bold uppercase tracking-[0.14em] text-[#c7d8bb]">Review queue</span>
              <strong className="mt-2 block text-3xl font-black tracking-[-0.04em] text-[#f7fcef]">{flaggedApplications.length}</strong>
            </div>
            <div className="rounded-[24px] border border-white/10 bg-white/5 px-4 py-4">
              <span className="text-xs font-bold uppercase tracking-[0.14em] text-[#c7d8bb]">Cleared cases</span>
              <strong className="mt-2 block text-3xl font-black tracking-[-0.04em] text-[#f7fcef]">{approvedApplications.length}</strong>
            </div>
          </div>
        </aside>

          <SectionCard
            eyebrow="Quick actions"
            subtitle="Shortcuts for the demo flow so you can move from dashboard to review with one click."
            title="Desk shortcuts"
          >
            <div className="grid gap-4">
              <Link
                className="rounded-[28px] border border-black/10 bg-white/75 p-5 transition duration-200 hover:-translate-y-1 hover:border-[#9fe870]/40 hover:bg-white"
                href="#create-application"
              >
                <strong>Start new application</strong>
                <span className="mt-2 block text-sm leading-6 text-[#454745]">Create a fresh case and move files into intake.</span>
              </Link>
              <Link
                className="rounded-[28px] border border-black/10 bg-white/75 p-5 transition duration-200 hover:-translate-y-1 hover:border-[#9fe870]/40 hover:bg-white"
                href={reviewCandidate?.next_review_document_id ? `/review/${reviewCandidate.next_review_document_id}` : "/applications"}
              >
                <strong>Continue last review</strong>
                <span className="mt-2 block text-sm leading-6 text-[#454745]">
                  {reviewCandidate?.next_review_document_file_name
                    ? `Resume ${reviewCandidate.next_review_document_file_name}`
                    : "Open the dashboard once a flagged document exists."}
                </span>
              </Link>
            </div>
          </SectionCard>
        </div>
      </div>
    </>
  );
}
