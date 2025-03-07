import { useState, useEffect, FC } from "react";
import {
  evaluateWebsite,
  evaluateWebsiteAI,
  getHeuristics,
  Heuristic,
} from "../../services/api";
import "./EvaluationForm.css";

interface EvaluationFormProps {
  onEvaluationComplete: (evaluationId: string, useAI: boolean) => void;
}

const EvaluationForm: FC<EvaluationFormProps> = ({ onEvaluationComplete }) => {
  const [url, setUrl] = useState("");
  const [maxPages, setMaxPages] = useState(2);
  const [depth, setDepth] = useState(2);
  const [selectedHeuristics, setSelectedHeuristics] = useState<string[]>([]);
  const [availableHeuristics, setAvailableHeuristics] = useState<Heuristic[]>(
    []
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHeuristics = async () => {
      try {
        const heuristics = await getHeuristics();
        setAvailableHeuristics(heuristics);
        // Select all heuristics by default
        setSelectedHeuristics(heuristics.map((h) => h._id));
      } catch (err) {
        setError("Failed to load heuristics. Please try again.");
        console.error(err);
      }
    };

    fetchHeuristics();
  }, []);

  const handleSubmit = async (e: React.FormEvent, useAI: boolean = false) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      let response;
      if (useAI) {
        response = await evaluateWebsiteAI({
          url,
          max_pages: maxPages,
          depth,
          heuristics: selectedHeuristics,
        });
      } else {
        response = await evaluateWebsite({
          url,
          max_pages: maxPages,
          depth,
          heuristics: selectedHeuristics,
        });
      }
      onEvaluationComplete(response.evaluation_id, useAI);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unknown error occurred"
      );
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleHeuristic = (id: string) => {
    if (selectedHeuristics.includes(id)) {
      setSelectedHeuristics(selectedHeuristics.filter((h) => h !== id));
    } else {
      setSelectedHeuristics([...selectedHeuristics, id]);
    }
  };

  return (
    <div className="evaluation-form-container">
      <h2 className="section-title">Evaluate Website UX</h2>

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit} className="card">
        <div className="form-group">
          <label htmlFor="url">Website URL</label>
          <input
            type="url"
            id="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="maxPages">Max Pages</label>
            <input
              type="number"
              id="maxPages"
              value={maxPages}
              onChange={(e) => setMaxPages(parseInt(e.target.value))}
              min="1"
              max="20"
            />
          </div>

          <div className="form-group">
            <label htmlFor="depth">Crawl Depth</label>
            <input
              type="number"
              id="depth"
              value={depth}
              onChange={(e) => setDepth(parseInt(e.target.value))}
              min="1"
              max="5"
            />
          </div>
        </div>

        <button
          type="submit"
          onClick={(e) => handleSubmit(e, true)}
          disabled={isLoading}
        >
          {isLoading ? "Evaluating With AI..." : "Evaluate With AI"}
        </button>
      </form>
    </div>
  );
};

export default EvaluationForm;
