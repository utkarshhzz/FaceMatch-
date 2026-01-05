import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { Calendar, TrendingUp, Clock, CheckCircle, XCircle, AlertCircle, BarChart3 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import api from "../services/api";

export default function EmployeeDashboard() {
    const { user } = useAuth();
    const [analytics, setAnalytics] = useState(null);
    const [records, setRecords] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAttendanceData();
    }, []);

    const fetchAttendanceData = async () => {
        try {
            const [analyticsRes, recordsRes] = await Promise.all([
                api.get("/faces/attendance/analytics"),
                api.get("/faces/attendance/my-records?limit=30")
            ]);

            setAnalytics(analyticsRes.data);
            setRecords(recordsRes.data);
        } catch (error) {
            console.error("Error fetching attendance:", error);
            toast.error("Failed to load attendance data");
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            weekday: 'short', 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    };

    const formatTime = (dateTimeString) => {
        if (!dateTimeString) return "-";
        const date = new Date(dateTimeString);
        return date.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    };

    const getStatusBadge = (status) => {
        const statusConfig = {
            present: { icon: CheckCircle, color: "text-green-600 bg-green-50 dark:bg-green-950", label: "Present" },
            absent: { icon: XCircle, color: "text-red-600 bg-red-50 dark:bg-red-950", label: "Absent" },
            half_day: { icon: AlertCircle, color: "text-yellow-600 bg-yellow-50 dark:bg-yellow-950", label: "Half Day" },
            leave: { icon: AlertCircle, color: "text-blue-600 bg-blue-50 dark:bg-blue-950", label: "Leave" }
        };

        const config = statusConfig[status] || statusConfig.present;
        const Icon = config.icon;

        return (
            <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
                <Icon className="h-3 w-3" />
                {config.label}
            </div>
        );
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-6">
            <div className="max-w-7xl mx-auto space-y-6">
                {/* Header */}
                <div className="space-y-2">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent">
                        My Attendance
                    </h1>
                    <p className="text-muted-foreground">
                        Welcome back, {user?.full_name || user?.email}!
                    </p>
                </div>

                {/* Analytics Cards */}
                {analytics && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {/* Attendance Percentage */}
                        <Card>
                            <CardHeader className="pb-3">
                                <CardTitle className="text-sm font-medium flex items-center gap-2">
                                    <TrendingUp className="h-4 w-4 text-blue-600" />
                                    Attendance Rate
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold text-blue-600">
                                    {analytics.attendance_percentage}%
                                </div>
                                <p className="text-xs text-muted-foreground mt-1">
                                    Overall performance
                                </p>
                            </CardContent>
                        </Card>

                        {/* Total Days */}
                        <Card>
                            <CardHeader className="pb-3">
                                <CardTitle className="text-sm font-medium flex items-center gap-2">
                                    <Calendar className="h-4 w-4 text-green-600" />
                                    Present Days
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold text-green-600">
                                    {analytics.present_days}
                                </div>
                                <p className="text-xs text-muted-foreground mt-1">
                                    Out of {analytics.total_days} total days
                                </p>
                            </CardContent>
                        </Card>

                        {/* Current Month */}
                        <Card>
                            <CardHeader className="pb-3">
                                <CardTitle className="text-sm font-medium flex items-center gap-2">
                                    <BarChart3 className="h-4 w-4 text-purple-600" />
                                    This Month
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold text-purple-600">
                                    {analytics.current_month_present}
                                </div>
                                <p className="text-xs text-muted-foreground mt-1">
                                    Out of {analytics.current_month_total} days
                                </p>
                            </CardContent>
                        </Card>

                        {/* Absent Days */}
                        <Card>
                            <CardHeader className="pb-3">
                                <CardTitle className="text-sm font-medium flex items-center gap-2">
                                    <XCircle className="h-4 w-4 text-red-600" />
                                    Absent Days
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold text-red-600">
                                    {analytics.absent_days}
                                </div>
                                <p className="text-xs text-muted-foreground mt-1">
                                    {analytics.half_days} half days, {analytics.leave_days} leaves
                                </p>
                            </CardContent>
                        </Card>
                    </div>
                )}

                {/* Attendance Records */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Clock className="h-5 w-5" />
                            Recent Attendance Records
                        </CardTitle>
                        <CardDescription>
                            Your last 30 days of attendance
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {records.length > 0 ? (
                            <div className="space-y-2">
                                {records.map((record) => (
                                    <div
                                        key={record.id}
                                        className="flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className="flex flex-col">
                                                <span className="font-medium">
                                                    {formatDate(record.date)}
                                                </span>
                                                <span className="text-sm text-muted-foreground">
                                                    {formatTime(record.time_in)}
                                                </span>
                                            </div>
                                        </div>
                                        
                                        <div className="flex items-center gap-4">
                                            {record.time_out && (
                                                <div className="text-right">
                                                    <span className="text-sm text-muted-foreground">Out: </span>
                                                    <span className="text-sm font-medium">
                                                        {formatTime(record.time_out)}
                                                    </span>
                                                </div>
                                            )}
                                            {getStatusBadge(record.status)}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-12 text-muted-foreground">
                                <Calendar className="h-12 w-12 mx-auto mb-3 opacity-50" />
                                <p>No attendance records yet</p>
                                <p className="text-sm mt-1">Mark your first attendance at the live camera station</p>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
