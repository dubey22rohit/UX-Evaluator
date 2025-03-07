import "./App.css";
import { ThemeProvider } from "./context/ThemeContext";
import AppRoutes from "./Routes";

function App() {
  return (
    <ThemeProvider>
      <AppRoutes />
    </ThemeProvider>
  );
}

export default App;
