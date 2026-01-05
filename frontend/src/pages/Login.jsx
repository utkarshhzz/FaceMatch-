import { useState } from "react";
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from "../context/AuthContext";
import { Lock, Mail, Eye, EyeOff, Loader2, IdCard } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { ModeToggle } from "@/components/mode-toggle";

export default function Login() {
    const [identifier, setIdentifier] = useState(''); // Can be email or employee_id
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            // Determine if identifier is email or employee_id
            const isEmail = identifier.includes('@');
            const loginData = isEmail 
                ? { email: identifier, password }
                : { employee_id: identifier, password };
                
            const success = await login(loginData);
            
            if (success) {
                // Small delay to ensure user state is loaded
                setTimeout(() => {
                    navigate('/dashboard');
                }, 100);
            }
        } catch (error) {
            console.error('Login error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 dark:from-indigo-950 dark:via-purple-950 dark:to-pink-950 flex items-center justify-end pr-10 overflow-hidden">
            
            {/* Theme Toggle Button - Top Left */}
            <div className="absolute top-4 left-4 z-20">
                <ModeToggle />
            </div>

            {/* Animated Background Blobs */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-white/10 dark:bg-white/5 rounded-full blur-3xl animate-pulse"></div>
                <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-white/10 dark:bg-white/5 rounded-full blur-3xl animate-pulse delay-700"></div>
            </div>

            {/* Login Card */}
            <Card className="w-full max-w-md relative z-10 shadow-2xl border-none dark:bg-slate-900">
                <CardHeader className="space-y-1 text-center">
                    {/* Logo */}
                    <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
                        <Lock className="h-8 w-8 text-white" />
                    </div>
                    
                    {/* Title */}
                    <CardTitle className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
                        FaceMatch++
                    </CardTitle>
                    
                    {/* Subtitle */}
                    <CardDescription className="text-base">
                        Sign in to access your account
                    </CardDescription>
                </CardHeader>

                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-4">
                        
                        {/* Email or Employee ID Field */}
                        <div className="space-y-2">
                            <Label htmlFor="identifier" className="text-sm font-medium">
                                Employee ID or Email
                            </Label>
                            <div className="relative">
                                <IdCard className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                                <Input
                                    id="identifier"
                                    type="text"
                                    placeholder="Employee ID or email"
                                    value={identifier}
                                    onChange={(e) => setIdentifier(e.target.value)}
                                    className="pl-10"
                                    required
                                />
                            </div>
                        </div>

                        {/* Password Field */}
                        <div className="space-y-2">
                            <Label htmlFor="password" className="text-sm font-medium">
                                Password
                            </Label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                                <Input
                                    id="password"
                                    type={showPassword ? "text" : "password"}
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="pl-10 pr-10"
                                    required
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-3 text-muted-foreground hover:text-foreground transition-colors"
                                >
                                    {showPassword ? (
                                        <EyeOff className="h-5 w-5" />
                                    ) : (
                                        <Eye className="h-5 w-5" />
                                    )}
                                </button>
                            </div>
                        </div>

                        {/* Forgot Password Link */}
                        <div className="flex justify-end">
                            <Link 
                                to="/forgot-password" 
                                className="text-sm text-primary hover:underline font-medium"
                            >
                                Forgot password?
                            </Link>
                        </div>

                        {/* Login Button */}
                        <Button 
                            type="submit" 
                            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-lg" 
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Signing in...
                                </>
                            ) : (
                                'Sign In'
                            )}
                        </Button>

                        {/* Divider */}
                        <div className="relative">
                            <div className="absolute inset-0 flex items-center">
                                <span className="w-full border-t" />
                            </div>
                            <div className="relative flex justify-center text-xs uppercase">
                                <span className="bg-background px-2 text-muted-foreground">
                                    Or continue with
                                </span>
                            </div>
                        </div>

                        {/* Google Login Button (Placeholder) */}
                        <Button 
                            type="button" 
                            variant="outline" 
                            className="w-full"
                            disabled
                        >
                            <svg className="mr-2 h-5 w-5" viewBox="0 0 24 24">
                                <path
                                    fill="currentColor"
                                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                                />
                                <path
                                    fill="currentColor"
                                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                                />
                                <path
                                    fill="currentColor"
                                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                                />
                                <path
                                    fill="currentColor"
                                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                                />
                            </svg>
                            Continue with Google (Coming Soon)
                        </Button>

                    </CardContent>

                    <CardFooter className="flex flex-col space-y-4">
                        <p className="text-center text-sm text-muted-foreground">
                            Don't have an account?{' '}
                            <Link to="/register" className="text-primary hover:underline font-semibold">
                                Create Account
                            </Link>
                        </p>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}