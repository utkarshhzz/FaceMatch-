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

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    <Card className="hover:shadow-lg transition-shadow cursor-pointer border-2 hover:border-indigo-500">
                        <CardHeader>
                            <div className="flex items-center gap-3">
                                <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-indigo-500 to-indigo-600 flex items-center justify-center">
                                    <Upload className="h-6 w-6 text-white"></Upload>
                                </div>
                                <div>
                                    <CardTitle>Register New Face</CardTitle>
                                    <CardDescription>Upload and register a new face</CardDescription>
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <Button className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700" onClick={() => navigate('/register-face')}>
                                Start Registration

                            </Button>
                        </CardContent>
                    </Card>


                    <Card className="hover: shadow-lg transition-shadow cursor-pointer border-2 hover:border-purple-500">
                        <CardHeader>
                            <div className="flex items-center gap-3">
                                <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
                                    <Search className="h-6 w-6 text-white"></Search>
                                    
                                    </div>

                            </div>
                            <CardTitle>Match Face</CardTitle>
                            <CardDescription>Find matching faces in database</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Button 
                                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                                onClick={() => navigate('/match-face')}
                            >
                                Start Matching
                            </Button>
                        </CardContent>
                         </Card>
                </div>


                {/* Statistics Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    {/* Total Faces */}
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">
                                Total Faces Registered
                            </CardTitle>
                            <Users className="h-4 w-4 text-muted-foreground"></Users>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{stats.totalFaces}</div>
                            <p className="text-xs text-muted-foreground">
                                Registered in your account
                            </p>
                        </CardContent>

                    </Card>

                    {/* Matches Found */}
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 ">
                            <CardTitle className="text-sm font-medium">Matches found</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{stats.matchesFound}</div>
                            <p className="text-xs text-muted-foreground"> Successful Face matches</p>
                        </CardContent>
                    </Card>

                    {/* Recent Activity */}
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">
                                Recent Activity
                            </CardTitle>
                            <Activity className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{stats.recentActivity.length}</div>
                            <p className="text-xs text-muted-foreground">
                                Actions in last 7 days
                            </p>
                        </CardContent>
                    </Card>
                    </div>

                {/* Recent Activity Feed */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Clock className="h-5 w-5" />
                            Recent Activity
                        </CardTitle>
                        <CardDescription>Your latest face recognition activities</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {stats.recentActivity.length === 0 ? (
                            <div className="text-center py-12">
                                <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                                <p className="text-muted-foreground">No recent activity</p>
                                <p className="text-sm text-muted-foreground">
                                    Start by registering or matching faces
                                </p>
                            </div>
                        ): (
                            <div className="space-y-4">
                                {stats.recentActivity.map((activity, index) => (
                                    <div key={index} className="flex items-center gap-4 p-3 rounded-lg bg-slate-50 dark:bg-slate-800">
                                        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                                            {activity.type === 'register' ? (
                                                <Upload className="h-5 w-5 text-white" />
                                            ) : (
                                                <Search className="h-5 w-5 text-white" />
                                            )}
                                        </div>
                                        <div className="flex-1">
                                            <p className="text-sm font-medium">{activity.title}</p>
                                            <p className="text-xs text-muted-foreground">{activity.time}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                        </CardContent>
                        </Card>
            </main>
                </div>
        
    );
}