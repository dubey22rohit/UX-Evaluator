import { FC } from "react";
import "./LoadingSpinner.css";

interface LoadingSpinnerProps {
  text?: string;
}

const LoadingSpinner: FC<LoadingSpinnerProps> = ({ text = "Loading..." }) => {
  return (
    <div className="loading-container">
      <div className="spinner"></div>
      <p className="loading-text pulse">{text}</p>
    </div>
  );
};

export default LoadingSpinner;
