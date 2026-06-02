import { createContext, useContext, useState } from "react";
import { getStoredUser, setAuth as persist, clearAuth } from "../services/api";

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [user, setUser] = useState(getStoredUser);
  const [currentSession, setCurrentSession] = useState(null);
  const [isLimitReached, setIsLimitReached] = useState(false);

  const login = ({ accessToken, user: userData }) => {
    persist({ accessToken, user: userData });
    setUser(userData);
  };

  const logout = () => {
    clearAuth();
    setUser(null);
    setCurrentSession(null);
    setIsLimitReached(false);
  };

  return (
    <AppContext.Provider
      value={{
        user,
        setUser,
        currentSession,
        setCurrentSession,
        isLimitReached,
        setIsLimitReached,
        login,
        logout,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export const useApp = () => useContext(AppContext);
