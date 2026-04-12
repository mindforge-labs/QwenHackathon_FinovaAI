"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import { SectionCard } from "@/components/common/section-card";
import { StatusBadge } from "@/components/common/status-badge";
import { useApplications } from "@/hooks/useApplications";
import { formatDate } from "@/lib/utils";

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

  return (
    <>
      <section className="hero">
        <h1>Review lending documents before risk reaches ops.</h1>
        <p>
          Upload ID cards, payslips, and bank statements. Process them with OCR and LLM extraction.
          Route mismatches and low-confidence cases into human review.
        </p>
      </section>

      <div className="dashboard-grid">
        <SectionCard title="Create Application" subtitle="Kick off a new lending intake case.">
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

        <SectionCard title="Applications" subtitle="Open an application to upload files and inspect document states.">
          {loading ? <p>Loading applications...</p> : null}
          {error ? <p className="feedback feedback-error">{error}</p> : null}
          <div className="application-list">
            {items.map((application) => (
              <Link className="application-card" href={`/applications/${application.id}`} key={application.id}>
                <div>
                  <h3>{application.applicant_name || "Untitled application"}</h3>
                  <p>{application.email || application.phone || "No contact info yet"}</p>
                  <p>{formatDate(application.created_at)}</p>
                </div>
                <StatusBadge status={application.status} />
              </Link>
            ))}
            {!loading && items.length === 0 ? <p>No applications yet.</p> : null}
          </div>
        </SectionCard>
      </div>
    </>
  );
}
