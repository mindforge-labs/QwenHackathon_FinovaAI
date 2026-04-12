"use client";

import { useEffect, useState } from "react";

import { createApplication, listApplications } from "@/lib/api";
import { ApplicationSummary } from "@/lib/types";

export function useApplications() {
  const [items, setItems] = useState<ApplicationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const response = await listApplications();
      setItems(response.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load applications.");
    } finally {
      setLoading(false);
    }
  }

  async function addApplication(payload: {
    applicant_name?: string;
    phone?: string;
    email?: string;
  }) {
    await createApplication(payload);
    await refresh();
  }

  useEffect(() => {
    void refresh();
  }, []);

  return { items, loading, error, refresh, addApplication };
}
