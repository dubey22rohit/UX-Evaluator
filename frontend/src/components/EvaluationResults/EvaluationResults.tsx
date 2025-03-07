import { useState, useEffect, FC } from "react";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { Pie } from "react-chartjs-2";
import {
  getEvaluationResults,
  generateReport,
  EvaluationResult,
} from "../../services/api";
import "./EvaluationResults.css";
import LoadingSpinner from "../LoadingSpinner";

ChartJS.register(ArcElement, Tooltip, Legend);

interface EvaluationResultsProps {
  evaluationId: string;
  onGenerateReport: () => void;
}

const EvaluationResults: FC<EvaluationResultsProps> = ({
  evaluationId,
  onGenerateReport,
}) => {
  const [results, setResults] = useState<EvaluationResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [reportGenerated, setReportGenerated] = useState(false);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data = await getEvaluationResults(evaluationId);
        console.log(`results data`, data);
        setResults(data);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load evaluation results"
        );
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [evaluationId]);

  const handleGenerateReport = async () => {
    setIsGeneratingReport(true);
    setError(null);

    try {
      await generateReport(evaluationId);
      setReportGenerated(true);
      setTimeout(() => {
        onGenerateReport();
      }, 1500);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate report"
      );
      console.error(err);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  const getSeverityClass = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical":
      case "high":
        return "error";
      case "medium":
        return "warning";
      case "low":
        return "success";
      default:
        return "";
    }
  };

  if (isLoading) {
    return <LoadingSpinner text="Loading report..." />;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!results) {
    return <div className="error-message">No results found</div>;
  }

  // Sort issues by severity
  const sortedIssues = [...results.issues].sort((a, b) => {
    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    return (
      (severityOrder[a.severity.toLowerCase() as keyof typeof severityOrder] ||
        4) -
      (severityOrder[b.severity.toLowerCase() as keyof typeof severityOrder] ||
        4)
    );
  });

  return (
    <div className="evaluation-results-container dark-theme">
      <div className="results-header">
        <h2 className="section-title">Evaluation Results</h2>
        <button
          onClick={handleGenerateReport}
          disabled={isGeneratingReport || reportGenerated}
          className={`generate-btn ${reportGenerated ? "success" : ""}`}
        >
          {reportGenerated
            ? "Report Generated!"
            : isGeneratingReport
            ? "Generating..."
            : "Generate Report"}
        </button>
      </div>

      <div className="card evaluation-summary">
        <h3>Summary</h3>
        <div className="summary-stats">
          <div className="stat-item">
            <div className="stat-icon pages-icon"></div>
            <span className="stat-value">{results.pages_analyzed}</span>
            <span className="stat-label">Pages Analyzed</span>
          </div>
          <div className="stat-item">
            <div className="stat-icon issues-icon"></div>
            <span className="stat-value">{results.issues.length}</span>
            <span className="stat-label">Issues Found</span>
          </div>
          <div className="stat-item">
            <div className="stat-icon date-icon"></div>
            <span className="stat-value">
              {new Date(results.timestamp).toLocaleDateString()}
            </span>
            <span className="stat-label">Evaluation Date</span>
          </div>
        </div>

        <div className="severity-chart-container">
          <h4>Issues by Severity</h4>
          <div
            className="severity-chart"
            style={{ width: "30%", margin: "0 auto" }}
          >
            <Pie
              data={{
                labels: ["High", "Medium", "Low"],
                datasets: [
                  {
                    data: [
                      results.issues.filter(
                        (i) => i.severity.toLowerCase() === "high"
                      ).length,
                      results.issues.filter(
                        (i) => i.severity.toLowerCase() === "medium"
                      ).length,
                      results.issues.filter(
                        (i) => i.severity.toLowerCase() === "low"
                      ).length,
                    ],
                    backgroundColor: ["#ef4444", "#f97316", "#22c55e"],
                    borderColor: ["#dc2626", "#ea580c", "#16a34a"],
                    borderWidth: 1,
                  },
                ],
              }}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: "bottom",
                    labels: {
                      color: "#e5e7eb",
                      font: {
                        size: 10,
                      },
                    },
                  },
                  tooltip: {
                    backgroundColor: "rgba(0, 0, 0, 0.8)",
                    titleColor: "#e5e7eb",
                    bodyColor: "#e5e7eb",
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                      label: (context) => {
                        const value = context.raw;
                        const total = context.dataset.data.reduce(
                          (a: number, b: number) => a + b,
                          0
                        );
                        const percentage = (
                          ((value as number) / total) *
                          100
                        ).toFixed(1);
                        return `${context.label}: ${value} (${percentage}%)`;
                      },
                    },
                  },
                },
              }}
            />
          </div>
        </div>
      </div>

      <div className="card issues-container">
        <h3>Issues Found</h3>
        {results.issues.length === 0 ? (
          <div className="no-issues-card">
            <div className="success-icon"></div>
            <p className="no-issues">No issues found. Great job!</p>
          </div>
        ) : (
          <div className="issues-list">
            {sortedIssues.map((issue, index) => (
              <div
                key={index}
                className={`issue-card ${getSeverityClass(issue.severity)}`}
              >
                <div className="issue-header">
                  <div className="issue-type">
                    <div
                      className={`severity-indicator ${getSeverityClass(
                        issue.severity
                      )}`}
                    ></div>
                    <h4>{issue.type}</h4>
                  </div>
                  <span
                    className={`severity-badge ${getSeverityClass(
                      issue.severity
                    )}`}
                  >
                    {issue.severity}
                  </span>
                </div>

                <div className="issue-content">
                  <p className="issue-description">{issue.description}</p>

                  <div className="issue-details">
                    <div className="detail-row url-row">
                      <div className="detail-icon url-icon"></div>
                      <div className="detail-content">
                        <strong>URL:</strong>
                        <a
                          href={issue.page_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="issue-link"
                        >
                          {issue.page_url}
                        </a>
                      </div>
                    </div>

                    {issue.element && (
                      <div className="detail-row element-row">
                        <div className="detail-icon element-icon"></div>
                        <div className="detail-content">
                          <strong>Element:</strong>
                          <code className="element-code">{issue.element}</code>
                        </div>
                      </div>
                    )}

                    {issue.recommendation && (
                      <div className="detail-row recommendation-row">
                        <div className="detail-icon recommendation-icon"></div>
                        <div className="detail-content">
                          <strong>Recommendation:</strong>
                          <p className="recommendation-text">
                            {issue.recommendation}
                          </p>
                        </div>
                      </div>
                    )}

                    {issue.heuristic && (
                      <div className="detail-row heuristic-row">
                        <div className="detail-icon heuristic-icon"></div>
                        <div className="detail-content">
                          <strong>Heuristic:</strong>
                          <p className="heuristic-text">{issue.heuristic}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default EvaluationResults;
