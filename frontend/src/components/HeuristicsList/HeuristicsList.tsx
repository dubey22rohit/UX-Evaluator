import { useState, useEffect, FC } from "react";
import { getHeuristics, Heuristic } from "../../services/api";
import LoadingSpinner from "../LoadingSpinner";
import "./HeuristicsList.css";

const HeuristicsList: FC = () => {
  const [heuristics, setHeuristics] = useState<Heuristic[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  useEffect(() => {
    const fetchHeuristics = async () => {
      try {
        const data = await getHeuristics();
        setHeuristics(data);

        // Set the first category as active by default
        if (data.length > 0) {
          const categories = [...new Set(data.map((h) => h.category))];
          if (categories.length > 0) {
            setActiveCategory(categories[0]);
          }
        }
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load heuristics"
        );
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHeuristics();
  }, []);

  const getCategories = () => {
    return [...new Set(heuristics.map((h) => h.category))];
  };

  const getHeuristicsByCategory = (category: string) => {
    return heuristics.filter((h) => h.category === category);
  };

  if (isLoading) {
    return <LoadingSpinner text="Loading heuristics..." />;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (heuristics.length === 0) {
    return <div className="error-message">No heuristics found</div>;
  }

  const categories = getCategories();

  return (
    <div className="heuristics-container">
      <h2 className="section-title">UX Heuristics</h2>

      <div className="heuristics-content">
        <div className="categories-sidebar">
          <h3>Categories</h3>
          <ul className="categories-list">
            {categories.map((category) => (
              <li
                key={category}
                className={activeCategory === category ? "active" : ""}
                onClick={() => setActiveCategory(category)}
              >
                {category}
              </li>
            ))}
          </ul>
        </div>

        <div className="heuristics-main">
          {activeCategory && (
            <>
              <h3>{activeCategory}</h3>
              <div className="heuristics-grid">
                {getHeuristicsByCategory(activeCategory).map((heuristic) => (
                  <div key={heuristic._id} className="heuristic-card card">
                    <h4>{heuristic.name}</h4>
                    <p>{heuristic.description}</p>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default HeuristicsList;
