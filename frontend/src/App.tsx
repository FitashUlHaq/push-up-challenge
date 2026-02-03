import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { TableProvider } from "./contexts/TableContext";
import User from "./pages/User";
import Record from "./pages/Record";

function App() {
  return (
    <TableProvider>
      <div className="app-container">
        <main className="app-main">
          <Routes>
            <Route path="/user" element={<User />} />
            <Route path="/record" element={<Record />} />
            <Route path="/" element={<Navigate to="/user" replace />} />
            <Route path="*" element={<Navigate to="/user" replace />} />
          </Routes>
        </main>
      </div>
    </TableProvider>
  );
}
export default App;
