import { createContext, useContext, useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";

const AuthContext=createContext(null);

export const AuthProvider=({children})=>{

    const[user,setUser]=useState(null);
    const [token, setToken] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(()=>{
        const storeToken=localStorage.getItem("token");
        if(storeToken){
            setToken(storeToken);
            setUser(jwtDecode(storeToken));
        }
         setLoading(false);
    },[]);

    const registerToken=(jwtToken)=>{

    localStorage.setItem("token",jwtToken);
    setToken(jwtToken);
    setUser(jwtDecode(jwtToken));
    }

    const login=(jwttoken)=>{
        localStorage.setItem("token",jwttoken);
        setToken(jwttoken);
        setUser(jwtDecode(jwttoken));
    }

    

    const logout=()=>{
        localStorage.removeItem("token");
        setToken(null);
        setUser(null);
    }

    const value={
        user,
        token,
        login,
        logout,
        registerToken,
        userId: user?.userId,
        username: user?.sub,
        isAuthenticated: !!token
    }

    if(loading) return null;

    return(
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    )
}

export   const useAuth=()=>useContext(AuthContext);