import { useState,useEffect }  from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import {
    Logout,
    User,
    Upload,
    Search,
    Activity,
    Users,
    CheckCircle,
    Clock
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {Card,CardContent,CardHeader,CardTitle,CardDescription} from "@/components/ui/card";
import { Avatar,AvatarFallback } from "@/components/mode-toggle";


export default function Dashboard() {
    const {user,logout}=useAuth();
    const navigate= useNavigate();
    const [stats,setStats]=useState({
        totalFaces:0,
        matchesFound:0,
        recentActivity:[]
    });


    useEffect(()=>{
        //redirecting user if not logged in
        if(!user) {
            navigate('/login');
        }
    }, [user,navigate]);

    const handleLogout= () => {
        logout();
        navigate('/login');
    };


    //get user initials from avatar
    const getInitials= (name)=> {
        if (!name) return 'U';
        return name
            .split(' ')
            .map(word=> word[0])
            .join('')
            .toUpperCase()
            .slice(0,2);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
            {/* Top Navigation bar */}
            <nav className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        {/* logo nd title */}
                        <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                                <User className="h-6 w-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
                                    FaceMatch++
                                </h1>
                                <p className="text-xs text-muted-foreground">Dashboard</p>
                            </div>
                        </div>
                        {/* Right Side Actions */}
                        <div className="flex items-center gap-4">
                            <ModeToggle />
                            
                            {/* User Profile */}
                            <div className="flex items-center gap-3">
                                <Avatar className="h-9 w-9">
                                    <AvatarFallback className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white">
                                        {getInitials(user?.full_name)}
                                    </AvatarFallback>
                                </Avatar>
                                <div className="hidden md:block">
                                    <p className="text-sm font-medium">{user?.full_name}</p>
                                    <p className="text-xs text-muted-foreground">{user?.email}</p>
                                </div>
                            </div>

                            {/* Logout Button */}
                            <Button 
                                variant="outline" 
                                size="sm"
                                onClick={handleLogout}
                                className="gap-2"
                            >
                                <LogOut className="h-4 w-4" />
                                Logout
                            </Button>

                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto p-4 sm:p-6 lg:px-8 py-8">
                <div className="mb-8">
                    <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
                        Welcome back,{user?.full_name?.split(' ')[0]}!
                    </h2>
                    <p className="text-slate-600 dark:text-slate-400">
                        Manage your face recognition tasks and view your activity here.
                    </p>
                </div>
        </div>
    )
}