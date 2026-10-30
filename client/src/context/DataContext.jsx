import { createContext, useEffect, useState } from "react";
import { apiRequest } from "../utils/api";

export const DataContext = createContext();

export function DataProvider({ children }) {
  const [ocrData, setOcrData] = useState(null);
  useEffect(() => {
    apiRequest("/latest/").then((data) => data && setOcrData(data)).catch(() => {});
  }, []);

  return (
    <DataContext.Provider value={{ ocrData, setOcrData }}>
      {children}
    </DataContext.Provider>
  );
}

export default DataProvider;
