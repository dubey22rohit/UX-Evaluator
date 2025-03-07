import { useState, useEffect, FC } from "react";
import {
  generateReport,
  generateReportAI,
  getReport,
  Report,
} from "../../services/api";
import LoadingSpinner from "../LoadingSpinner";
import "./ReportView.css";
import { useParams } from "react-router-dom";

const ReportView = () => {
  const { evaluationId } = useParams<{ evaluationId: string }>();
  const [report, setReport] = useState<Report | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const data = await generateReportAI(evaluationId as string);
        console.log("generate report data", data);
        setReport(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load report");
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchReport();
  }, [evaluationId]);

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

  if (!report) {
    return <div className="error-message">No report found</div>;
  }

  return (
    <div className="report-container">
      <h2 className="section-title">UX Evaluation Report</h2>

      <div className="report-header card">
        <div className="report-meta">
          <h3>
            Website:{" "}
            <a href={report.url} target="_blank" rel="noopener noreferrer">
              {report.url}
            </a>
          </h3>
          <p>
            Evaluation Date: {new Date(report.timestamp).toLocaleDateString()}
          </p>
          <p>Report ID: {report.report_id}</p>
        </div>
      </div>

      <div className="report-summary card">
        <h3>Summary</h3>
        <div className="summary-stats">
          <div className="stat-item">
            <span className="stat-value">{report.summary.total_pages}</span>
            <span className="stat-label">Pages Analyzed</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{report.summary.total_issues}</span>
            <span className="stat-label">Issues Found</span>
          </div>
        </div>

        <div className="breakdown-section">
          <div className="breakdown-column">
            <h4>Issues by Severity</h4>
            <div className="breakdown-chart">
              {Object.entries(report.summary.severity_breakdown).map(
                ([severity, count]) => (
                  <div key={severity} className="breakdown-item">
                    <div className="breakdown-label">
                      <span className={`badge ${getSeverityClass(severity)}`}>
                        {severity}
                      </span>
                    </div>
                    <div className="breakdown-bar-container">
                      <div
                        className={`breakdown-bar ${getSeverityClass(
                          severity
                        )}`}
                        style={{
                          width: `${
                            (count / report.summary.total_issues) * 100
                          }%`,
                        }}
                      ></div>
                    </div>
                    <div className="breakdown-count">{count}</div>
                  </div>
                )
              )}
            </div>
          </div>

          <div className="breakdown-column">
            <h4>Issues by Category</h4>
            <div className="breakdown-chart">
              {Object.entries(report.summary.category_breakdown).map(
                ([category, count]) => (
                  <div key={category} className="breakdown-item">
                    <div className="breakdown-label">{category}</div>
                    <div className="breakdown-bar-container">
                      <div
                        className="breakdown-bar"
                        style={{
                          width: `${
                            (count / report.summary.total_issues) * 100
                          }%`,
                        }}
                      ></div>
                    </div>
                    <div className="breakdown-count">{count}</div>
                  </div>
                )
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="report-issues card">
        <h3>Detailed Issues</h3>

        {report.issues.length === 0 ? (
          <p className="no-issues">No issues found. Great job!</p>
        ) : (
          <div className="issues-list">
            {report.issues.map((issue, index) => (
              <div
                key={index}
                className={`issue-item ${getSeverityClass(issue.severity)}`}
              >
                <div className="issue-header">
                  <h4>{issue.type}</h4>
                  <span className={`badge ${getSeverityClass(issue.severity)}`}>
                    {issue.severity}
                  </span>
                </div>

                <p className="issue-description">{issue.description}</p>

                <div className="issue-details">
                  <div className="issue-url">
                    <strong>URL:</strong>{" "}
                    <a
                      href={issue.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {issue.url}
                    </a>
                  </div>
                  {issue.element && (
                    <div className="issue-element">
                      <strong>Element:</strong> <code>{issue.element}</code>
                    </div>
                  )}
                  <div className="issue-recommendation">
                    <strong>Recommendation:</strong> {issue.recommendation}
                  </div>
                </div>

                {issue.screenshot && (
                  <div className="issue-screenshot">
                    <h5>Screenshot</h5>
                    <img
                      src={`data:image/png;base64,${issue.screenshot}`}
                      alt="Issue screenshot"
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="report-recommendations card">
        <h3>Recommendations</h3>
        <ul className="recommendations-list">
          {report.recommendations.map((recommendation, index) => (
            <li key={index}>{recommendation}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ReportView;
