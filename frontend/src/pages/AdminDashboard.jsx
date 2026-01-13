import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { 
    Users, 
    UserPlus, 
    Activity, 
    Trash2, 
    Search, 
    ArrowLeft,
    Download,
    FileSpreadsheet,
    Camera
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import api from "@/services/api";

export default function AdminDashboard() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");
    const [isExporting, setIsExporting] = useState(false);

    // Export function
    const handleExport = async () => {
        setIsExporting(true);

        try {
            // API call
            const response = await api.get("/faces/attendance/export", {
                responseType: 'blob'
            });

            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;

            // Setting filename
            const filename = `attendance_report_${new Date().toISOString().split('T')[0]}.xlsx`;
            link.setAttribute('download', filename);

            // Trigger download
            document.body.appendChild(link);
            link.click();

            // Cleanup
            link.remove();
            window.URL.revokeObjectURL(url);

            toast.success("Report Downloaded Successfully!");
        } catch (error) {
            console.error("Export error:", error);
            toast.error("Failed to export report");
        } finally {
            setIsExporting(false);
        }
    };

    // Check if user is admin
    useEffect(() => {
        if (!user || user.role !== 'admin') {
            toast.error('Access denied. Admins only.');
            navigate('/dashboard');
        }
    }, [user, navigate]);

    // Fetch employees
    const fetchEmployees = async () => {
        try {
            setLoading(true);
            const response = await api.get('/faces/employees');
            setEmployees(response.data.employees);
        } catch (error) {
            console.error('Failed to fetch employees:', error);
            toast.error('Failed to load employees.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchEmployees();
    }, []);

    // Delete employee
    const handleDelete = async (employeeId) => {
        if (!confirm(`Delete employee ${employeeId}?`)) return;

        try {
            await api.delete(`/faces/employees/${employeeId}`);
            toast.success('Employee deleted successfully');
            fetchEmployees();
        } catch (error) {
            console.error('Failed to delete employee:', error);
            toast.error('Failed to delete employee');
        }
    };

    // Filter employees
    const filteredEmployees = employees.filter(emp =>
        emp.employee_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        emp.full_name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-950 dark:to-slate-900">
            {/* Header */}
            <div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-8 py-6">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
                            Admin Dashboard
                        </h1>
                        <p className="text-slate-600 dark:text-slate-400 mt-2">
                            Manage employee registrations and attendance
                        </p>
                    </div>
                    <div className="flex gap-3">
                        <Button
                            variant="outline"
                            onClick={() => navigate('/dashboard')}
                        >
                            <ArrowLeft className="h-4 w-4 mr-2" />
                            Back
                        </Button>
                        <Button
                            onClick={() => navigate('/register-face')}
                            variant="outline"
                        >
                            <UserPlus className="h-4 w-4 mr-2" />
                            Single Photo
                        </Button>
                        <Button
                            onClick={() => navigate('/register-multiple-faces')}
                            className="bg-gradient-to-r from-indigo-600 to-purple-600"
                        >
                            <Camera className="h-4 w-4 mr-2" />
                            Multiple Photos
                        </Button>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                
                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    {/* Total Employees Card */}
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">
                                Total Employees
                            </CardTitle>
                            <Users className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{employees.length}</div>
                            <p className="text-xs text-muted-foreground">
                                Registered in system
                            </p>
                        </CardContent>
                    </Card>

                    {/* Active Today Card */}
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">
                                Active Today
                            </CardTitle>
                            <Activity className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">0</div>
                            <p className="text-xs text-muted-foreground">
                                Attendance marked
                            </p>
                        </CardContent>
                    </Card>

                    {/* System Status Card */}
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">
                                System Status
                            </CardTitle>
                            <div className="h-3 w-3 bg-green-500 rounded-full animate-pulse" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">Online</div>
                            <p className="text-xs text-muted-foreground">
                                All systems operational
                            </p>
                        </CardContent>
                    </Card>
                </div>

                {/* Export Reports Card */}
                <Card className="mb-8">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <FileSpreadsheet className="h-5 w-5" />
                            Export Reports
                        </CardTitle>
                        <CardDescription>
                            Download all attendance records as Excel file
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Button 
                            onClick={handleExport}
                            disabled={isExporting}
                            className="gap-2"
                        >
                            <Download className="h-4 w-4" />
                            {isExporting ? "Exporting..." : "Download Report"}
                        </Button>
                    </CardContent>
                </Card>

                {/* Employee List */}
                <Card>
                    <CardHeader>
                        <div className="flex justify-between items-center">
                            <div>
                                <CardTitle>Registered Employees</CardTitle>
                                <CardDescription>
                                    Manage employee face registrations
                                </CardDescription>
                            </div>
                            <div className="relative w-64">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="Search employees..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="pl-10"
                                />
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <div className="text-center py-12">
                                <p className="text-muted-foreground">Loading employees...</p>
                            </div>
                        ) : filteredEmployees.length === 0 ? (
                            <div className="text-center py-12">
                                <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                                <p className="text-muted-foreground">
                                    {searchQuery ? 'No employees match your search' : 'No employees registered yet'}
                                </p>
                                <Button
                                    onClick={() => navigate('/register-face')}
                                    className="mt-4"
                                >
                                    <UserPlus className="h-4 w-4 mr-2" />
                                    Register First Employee
                                </Button>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {filteredEmployees.map((emp) => (
                                    <div
                                        key={emp.id}
                                        className="flex items-center justify-between p-4 border rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className="h-12 w-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-semibold">
                                                {emp.full_name.split(' ').map(n => n[0]).join('').toUpperCase()}
                                            </div>
                                            <div>
                                                <h3 className="font-semibold">{emp.full_name}</h3>
                                                <p className="text-sm text-muted-foreground">
                                                    ID: {emp.employee_id}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                                                emp.is_active 
                                                    ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                                                    : 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                                            }`}>
                                                {emp.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => handleDelete(emp.employee_id)}
                                                className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}