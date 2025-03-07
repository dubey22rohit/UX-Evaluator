import { EvaluationResultAI, Screenshot } from "./types";

const API_BASE_URL = "http://localhost:8000/api";

export interface EvaluationRequest {
  url: string;
  max_pages: number;
  depth: number;
  heuristics: string[];
  custom_checks?: Record<string, any>[];
}

export interface EvaluationResponse {
  evaluation_id: string;
  status: string;
  message: string;
  pages_analyzed: number;
  issues_found: number;
}

export interface EvaluationResult {
  evaluation_id: string;
  url: string;
  timestamp: string;
  status: string;
  pages_analyzed: number;
  issues: Array<{
    type: string;
    heuristic: string;
    description: string;
    severity: string;
    page_url: string;
    element?: string;
    recommendation: string;
  }>;
}

export interface Heuristic {
  _id: string;
  name: string;
  description: string;
  category: string;
}

export interface Report {
  report_id: string;
  evaluation_id: string;
  url: string;
  timestamp: string;
  summary: {
    total_pages: number;
    total_issues: number;
    severity_breakdown: Record<string, number>;
    category_breakdown: Record<string, number>;
  };
  issues: Array<{
    type: string;
    severity: string;
    description: string;
    url: string;
    element?: string;
    recommendation: string;
    screenshot?: string;
  }>;
  recommendations: string[];
}

// Evaluate a website
export const evaluateWebsite = async (
  data: EvaluationRequest
): Promise<EvaluationResponse> => {
  const response = await fetch(`${API_BASE_URL}/evaluate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to evaluate website");
  }

  return response.json();
};

// Get evaluation results
export const getEvaluationResults = async (
  evaluationId: string
): Promise<EvaluationResult> => {
  const response = await fetch(`${API_BASE_URL}/evaluations/${evaluationId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get evaluation results");
  }

  return response.json();
};

// Generate report
export const generateReport = async (
  evaluationId: string
): Promise<{ message: string; report_id: string }> => {
  const response = await fetch(
    `${API_BASE_URL}/generate-report/${evaluationId}`,
    {
      method: "POST",
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to generate report");
  }

  return response.json();
};

// Get report
export const getReport = async (evaluationId: string): Promise<Report> => {
  const response = await fetch(`${API_BASE_URL}/reports/${evaluationId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get report");
  }

  return response.json();
};

// Get heuristics
export const getHeuristics = async (): Promise<Heuristic[]> => {
  const response = await fetch(`${API_BASE_URL}/heuristics`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get heuristics");
  }

  return response.json();
};

// Evaluate a website using AI
export const evaluateWebsiteAI = async (
  data: EvaluationRequest
): Promise<EvaluationResponse> => {
  const response = await fetch(`${API_BASE_URL}/evaluate-ai`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to evaluate website using AI");
  }

  return response.json();
};

// Get AI evaluation results
export const getEvaluationResultsAI = async (
  evaluationId: string
): Promise<EvaluationResultAI> => {
  const response = await fetch(
    `${API_BASE_URL}/evaluations-ai/${evaluationId}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get AI evaluation results");
  }

  return response.json();
};

// Generate AI report
export const generateReportAI = async (
  evaluationId: string
): Promise<{ message: string; report_id: string }> => {
  const response = await fetch(
    `${API_BASE_URL}/generate-report-ai/${evaluationId}`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to generate AI report");
  }

  return response.json();
};

// Get AI report
export const getReportAI = async (evaluationId: string): Promise<Report> => {
  const response = await fetch(`${API_BASE_URL}/reports-ai/${evaluationId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get AI report");
  }

  return response.json();
};

// Get AI screenshot
export const getScreenshotAI = async (evaluationId: string): Promise<Blob> => {
  const response = await fetch(
    `${API_BASE_URL}/get-screenshot-ai/${evaluationId}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get screenshots");
  }

  return response.blob();
};
