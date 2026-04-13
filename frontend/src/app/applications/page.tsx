"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import { MetricCard } from "@/components/common/metric-card";
import { PipelineStrip } from "@/components/common/pipeline-strip";
import { ProgressMeter } from "@/components/common/progress-meter";
import { SectionCard } from "@/components/common/section-card";
import { StatusBadge } from "@/components/common/status-badge";
import { useApplications } from "@/hooks/useApplications";
import { ApplicationSummary } from "@/lib/types";
import { formatDate } from "@/lib/utils";

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
      <section className="hero hero--dashboard">
        <div className="hero__content">
          <div className="hero__body">
            <p className="eyebrow">AI risk review platform</p>
            <h1>Make the AI visible. Make the risk obvious. Make the human decision powerful.</h1>
            <p>
              Finova turns the intake desk into a live command center: upload files, watch OCR and
              extraction flow, then route risky cases into a decisive human review lane.
            </p>
            <div className="hero__actions">
              <Link className="button button-primary" href="#create-application">
                Start new application
              </Link>
              {reviewCandidate?.next_review_document_id ? (
                <Link
                  className="button button-secondary"
                  href={`/review/${reviewCandidate.next_review_document_id}`}
                >
                  Continue last review
                </Link>
              ) : (
                <Link className="button button-secondary" href="/applications">
                  Monitor queue
                </Link>
              )}
            </div>
          </div>

          <div className="hero__visual">
            <img alt="AI review command center" src="/Banknote-bro.png" />
          </div>
        </div>
      </section>

      <section className="metric-grid">
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

      <div className="dashboard-grid dashboard-grid--dashboard">
        <SectionCard
          eyebrow="Applications"
          subtitle="Grouped by urgency so the review desk can focus where risk is surfacing."
          title="Portfolio queue"
        >
          {loading ? <p>Loading applications...</p> : null}
          {error ? <p className="feedback feedback-error">{error}</p> : null}

          <div className="application-groups">
            {groups.map((group) => (
              <section className="application-group" key={group.key}>
                <header className="application-group__header">
                  <div>
                    <p className="eyebrow">{group.title}</p>
                    <h3>{group.items.length} case(s)</h3>
                  </div>
                  <p>{group.subtitle}</p>
                </header>

                <div className="application-list">
                  {group.items.map((application) => {
                    const totalDocsForApp = application.document_count;
                    const processedDocs = application.processed_document_count;
                    const flaggedDocs = application.flagged_document_count;
                    const progress = totalDocsForApp === 0 ? 0 : (processedDocs / totalDocsForApp) * 100;

                    return (
                      <Link className="application-card" href={`/applications/${application.id}`} key={application.id}>
                        <div className="application-card__header">
                          <div>
                            <h3>{application.applicant_name || "Untitled application"}</h3>
                            <p>{application.email || application.phone || "No contact info yet"}</p>
                          </div>
                          <div className="application-card__signals">
                            {flaggedDocs > 0 ? (
                              <span className="signal-pill signal-pill--danger">
                                {flaggedDocs} risk signal{flaggedDocs > 1 ? "s" : ""}
                              </span>
                            ) : (
                              <span className="signal-pill signal-pill--neutral">Clean scan</span>
                            )}
                            <StatusBadge status={application.status} />
                          </div>
                        </div>

                        <div className="application-card__meta">
                          <span>Created {formatDate(application.created_at)}</span>
                          <span>{totalDocsForApp} document(s)</span>
                          <span>{processedDocs} processed</span>
                        </div>

                        <ProgressMeter
                          label={
                            totalDocsForApp > 0
                              ? `${processedDocs}/${totalDocsForApp} documents processed`
                              : "Awaiting uploads"
                          }
                          tone={flaggedDocs > 0 ? "warning" : application.status === "approved" ? "positive" : "brand"}
                          value={progress}
                        />
                      </Link>
                    );
                  })}
                </div>
              </section>
            ))}

            {!loading && orderedItems.length === 0 ? <p className="empty-state">No applications yet.</p> : null}
          </div>
        </SectionCard>

        <div className="dashboard-sidebar">

          <SectionCard
            actions={<span className="signal-pill signal-pill--soft">{submitting ? "Creating..." : "Ready"}</span>}
            eyebrow="Quick action"
            id="create-application"
            subtitle="Kick off a new lending intake case from the dashboard."
            title="Create application"
          >
            <form className="create-form" onSubmit={(event) => void handleCreate(event)}>
              <label>
                Applicant Name
                <input
                  value={form.applicant_name}
                  onChange={(event) => setForm((current) => ({ ...current, applicant_name: event.target.value }))}
                />
              </label>
              <label>
                Phone
                <input
                  value={form.phone}
                  onChange={(event) => setForm((current) => ({ ...current, phone: event.target.value }))}
                />
              </label>
              <label className="form-grid__full">
                Email
                <input
                  value={form.email}
                  onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
                />
              </label>
              <div className="form-grid__full">
                <button className="button button-primary" disabled={submitting} type="submit">
                  {submitting ? "Creating..." : "Create Application"}
                </button>
              </div>
            </form>
          </SectionCard>

<aside className="hero__panel hero__panel--dark">
          <div className="hero__panel-header">
            <div>
              <p className="eyebrow eyebrow--inverse">Processing pipeline</p>
              <h2>Command center flow</h2>
            </div>
            <span className="signal-pill signal-pill--positive">Live</span>
          </div>
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
          <div className="hero-stats">
            <div>
              <span>Docs monitored</span>
              <strong>{totalDocuments}</strong>
            </div>
            <div>
              <span>Review queue</span>
              <strong>{flaggedApplications.length}</strong>
            </div>
            <div>
              <span>Cleared cases</span>
              <strong>{approvedApplications.length}</strong>
            </div>
          </div>
        </aside>

          <SectionCard
            eyebrow="Quick actions"
            subtitle="Shortcuts for the demo flow so you can move from dashboard to review with one click."
            title="Desk shortcuts"
          >
            <div className="quick-action-grid">
              <Link className="quick-action-card" href="#create-application">
                <strong>Start new application</strong>
                <span>Create a fresh case and move files into intake.</span>
              </Link>
              <Link
                className="quick-action-card"
                href={reviewCandidate?.next_review_document_id ? `/review/${reviewCandidate.next_review_document_id}` : "/applications"}
              >
                <strong>Continue last review</strong>
                <span>
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
