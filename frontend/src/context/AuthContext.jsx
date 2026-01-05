import { createContext,useContext,useState,useEffect } from "react";
import {authAPI} from '../services/api';
import { toast } from 'sonner';

const AuthContext=createContext(null);
export const AuthProvider=({children})=> {
    const [user,setUser]=useState(null);
    const [loading,setLoading]=useState(true);

    //checking if user is logged in on our app
    useEffect(() => {
        const token=localStorage.getItem('token');
        if(token) {
            loadUser();
        }
        else {
            setLoading(false);
        }
    }, []);

    //loading user data from backend agar user ka token hai toh
    const loadUser=async () => {
        try {
            const response =await authAPI.getCurrentUser();
            setUser(response.data);
        } catch(error) {
            console.error('Failed to load user',error);
            localStorage.removeItem('token');
        } finally {
            setLoading(false);
        }
    };

    //login function
    const login=async (loginData) => {
        try {
            const response= await authAPI.login(loginData);
            localStorage.setItem('token',response.data.access_token);
            await loadUser();
            toast.success('Login Successful',{
                description:'Welcome back!'});
            
            return true;
        } catch(error) {
            toast.error('Login Failed. Please check your credentials.');
            return false;
        }
    };

    //register function
    const register=async (email,password,fullName) => {
        try {
            await authAPI.register({
                email,
                password,
                full_name:fullName
            });
            toast.success('Registration Successful. Please login.');
            return true;
        } catch(error) {
            toast.error('Registration Failed. Please try again.');
            return false;
        }
    };
    //logout function
    const logout=() => {
        localStorage.removeItem('token');
        setUser(null);
        toast.info('Logged out successfully',{description:"See you soon!"});
    };

    return (
        <AuthContext.Provider value={{user,login,register,logout,loading}}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth=() => {
    const context=useContext(AuthContext);
    if(!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
}