interface Coordinates {
  x: number;
  y: number;
}

interface AnalysisResultItem {
  top_left_coordinates: Coordinates;
  top_right_coordinates: Coordinates;
  bottom_right_coordinates: Coordinates;
  bottom_left_coordinates: Coordinates;
  heuristic: string;
  description: string;
  severity: string;
  recommendation: string;
}

interface PageAnalysisResult {
  analysis_results: AnalysisResultItem[];
}

export interface EvaluationResultAI {
  evaluation_id: string;
  status: string;
  message: string;
  pages_analyzed: number;
  issues_found: number;
  analysis_results: PageAnalysisResult[];
}

export interface Screenshot {
  url: string;
  image: Blob;
  timestamp: string;
}
