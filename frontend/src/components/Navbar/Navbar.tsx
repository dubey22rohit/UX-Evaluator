import { FC } from "react";
import "./Navbar.css";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const Navbar: FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h1>UX Evaluation Tool</h1>
      </div>
      <ul className="navbar-nav">
        <li className={`nav-item ${activeTab === "evaluate" ? "active" : ""}`}>
          <button onClick={() => setActiveTab("evaluate")}>Evaluate</button>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
