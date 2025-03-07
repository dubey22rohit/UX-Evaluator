import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { useState } from "react";
import EvaluationForm from "./components/EvaluationForm";
import ReportView from "./components/ReportView";
import HeuristicsList from "./components/HeuristicsList";
import Navbar from "./components/Navbar";
import EvaluationResults from "./components/EvaluationResults";
import AIEvaluationResults from "./components/AIEvaluationResults";

const AppRoutes = () => {
  const [activeTab, setActiveTab] = useState("evaluate");

  return (
    <Router>
      <div className="app-container">
        <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
        <main className="content">
          <Routes>
            <Route
              path="/"
              element={
                <EvaluationForm
                  onEvaluationComplete={(id, useAI) => {
                    if (useAI) {
                      window.location.href = `/ai-results/${id}`;
                    } else {
                      window.location.href = `/results/${id}`;
                    }
                  }}
                />
              }
            />
            <Route
              path="/ai-results/:evaluationId"
              element={<AIEvaluationResults />}
            />
            <Route path="/report/:evaluationId" element={<ReportView />} />
            <Route path="/heuristics" element={<HeuristicsList />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default AppRoutes;
