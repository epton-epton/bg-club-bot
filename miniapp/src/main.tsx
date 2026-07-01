import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import App from "./App";
import { AppSettingsProvider } from "./contexts/AppSettingsContext";
import { ClubProvider } from "./contexts/ClubContext";
import "./themes.css";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AppSettingsProvider>
      <ClubProvider>
        <App />
      </ClubProvider>
    </AppSettingsProvider>
  </StrictMode>,
);
