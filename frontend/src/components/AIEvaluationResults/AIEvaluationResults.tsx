import { useState, useEffect, FC } from "react";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { Pie } from "react-chartjs-2";
import {
  generateReportAI,
  getEvaluationResultsAI,
  getScreenshotAI,
} from "../../services/api";
import "./AIEvaluationResults.css";
import LoadingSpinner from "../LoadingSpinner";
import { EvaluationResultAI } from "../../services/api/types";
import ImageAnnotator from "../ImageAnnotator";
import { useParams } from "react-router-dom";
import ChatBot from "../ChatBot/ChatBot";

ChartJS.register(ArcElement, Tooltip, Legend);

const AIEvaluationResults = () => {
  const { evaluationId } = useParams<{ evaluationId: string }>();

  const [results, setResults] = useState<EvaluationResultAI | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [reportGenerated, setReportGenerated] = useState(false);
  const [screenshots, setScreenshots] = useState<
    { url: string; imageUrl: string; timestamp: string }[]
  >([]);
  const [isChatOpen, setIsChatOpen] = useState<boolean>(false);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [selectedCardIndex, setSelectedCardIndex] = useState<number | null>(
    null
  );

  const handleCardClick = (index: number) => {
    setSelectedCardIndex(selectedCardIndex === index ? null : index);
  };

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const [data, screenshotData] = await Promise.all([
          getEvaluationResultsAI(evaluationId as string),
          getScreenshotAI(evaluationId as string),
        ]);
        const imageUrl = URL.createObjectURL(screenshotData);
        setImageUrl(imageUrl);
        setResults(data);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load AI evaluation results"
        );
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();

    // Cleanup function to revoke all URLs when component unmounts
    return () => {
      screenshots.forEach((screenshot) => {
        URL.revokeObjectURL(screenshot.imageUrl);
      });
    };
  }, [evaluationId]);

  const handleGenerateReport = async () => {
    setIsGeneratingReport(true);
    setError(null);

    try {
      await generateReportAI(evaluationId as string);
      setReportGenerated(true);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate AI report"
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
    return <LoadingSpinner text="Loading AI analysis..." />;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!results) {
    return <div className="error-message">No AI analysis results found</div>;
  }

  // Get all issues from all pages
  const allIssues = results.analysis_results.flatMap((page) =>
    page.analysis_results.map((issue) => ({
      ...issue,
      severity: issue.severity,
      type: issue.heuristic,
    }))
  );

  // Sort issues by severity
  const sortedIssues = [...allIssues].sort((a, b) => {
    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    return (
      (severityOrder[a.severity.toLowerCase() as keyof typeof severityOrder] ||
        4) -
      (severityOrder[b.severity.toLowerCase() as keyof typeof severityOrder] ||
        4)
    );
  });

  return (
    <>
      <div className="evaluation-results-container dark-theme">
        <div className="results-header">
          <h2 className="section-title">AI Evaluation Results</h2>
          <button
            onClick={handleGenerateReport}
            disabled={isGeneratingReport || reportGenerated}
            className={`generate-btn ${reportGenerated ? "success" : ""}`}
          >
            {reportGenerated
              ? "AI Report Generated!"
              : isGeneratingReport
              ? "Generating..."
              : "Generate AI Report"}
          </button>
        </div>

        <div className="card evaluation-summary">
          <h3>AI Analysis Summary</h3>
          <div className="summary-stats">
            <div className="stat-item">
              <div className="stat-icon pages-icon"></div>
              <span className="stat-value">{results.pages_analyzed}</span>
              <span className="stat-label">Pages Analyzed</span>
            </div>
            <div className="stat-item">
              <div className="stat-icon issues-icon"></div>
              <span className="stat-value">{allIssues?.length || 0}</span>
              <span className="stat-label">Issues Found</span>
            </div>
          </div>

          <div className="severity-chart-container">
            <h4>AI-Detected Issues by Severity</h4>
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
                        allIssues.filter(
                          (i) => i.severity.toLowerCase() === "high"
                        ).length,
                        allIssues.filter(
                          (i) => i.severity.toLowerCase() === "medium"
                        ).length,
                        allIssues.filter(
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
          <h3>AI-Detected Issues</h3>
          {sortedIssues.length === 0 ? (
            <div className="no-issues-card">
              <div className="success-icon"></div>
              <p className="no-issues">No issues detected by AI. Great job!</p>
            </div>
          ) : (
            <div className="issues-list">
              {sortedIssues.map((issue, index) => (
                <div
                  key={index}
                  className={`issue-card ${getSeverityClass(issue.severity)} ${
                    selectedCardIndex === index ? "expanded" : ""
                  }`}
                  onClick={() => handleCardClick(index)}
                >
                  <div className="issue-header">
                    <div className="issue-type">
                      <div
                        className={`severity-indicator ${getSeverityClass(
                          issue.severity
                        )}`}
                      ></div>
                      <h4>{issue.heuristic}</h4>
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
                      <div className="detail-row coordinates-row">
                        <div className="detail-icon coordinates-icon"></div>
                        <div className="detail-content">
                          <strong>Location:</strong>
                          <code className="coordinates-code">
                            x: {issue.top_left_coordinates.x}, y:{" "}
                            {issue.top_left_coordinates.y}
                          </code>
                        </div>
                      </div>

                      {issue.recommendation && (
                        <div className="detail-row recommendation-row">
                          <div className="detail-icon recommendation-icon"></div>
                          <div className="detail-content">
                            <strong>AI Recommendation:</strong>
                            <p className="recommendation-text">
                              {issue.recommendation}
                            </p>
                          </div>
                        </div>
                      )}

                      <div className="detail-row heuristic-row">
                        <div className="detail-icon heuristic-icon"></div>
                        <div className="detail-content">
                          <strong>Heuristic:</strong>
                          <p className="heuristic-text">{issue.heuristic}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  {imageUrl && selectedCardIndex === index && (
                    <div className="screenshot-container">
                      <ImageAnnotator
                        imageUrl={imageUrl as string}
                        annotations={[
                          {
                            top_left: issue.top_left_coordinates,
                            top_right: issue.top_right_coordinates,
                            bottom_right: issue.bottom_right_coordinates,
                            bottom_left: issue.bottom_left_coordinates,
                            label: issue.heuristic,
                          },
                        ]}
                        className="w-full rounded-lg shadow-lg"
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      <div className="ai-evaluation-results-container">
        <button
          className="chat-toggle-button"
          onClick={() => setIsChatOpen(!isChatOpen)}
        >
          {isChatOpen ? "Close Chat" : "Open Chat"}
        </button>
        {isChatOpen && (
          <div className="chat-window">
            <ChatBot evaluationId={evaluationId as string} />
          </div>
        )}
      </div>
    </>
  );
};

export default AIEvaluationResults;
