import { useState, useRef, useEffect } from "react";
import Webcam from "react-webcam";
import { Camera, UserCheck, X, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import api from "../services/api";

export default function LiveAttendance() {
    const webcamRef = useRef(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [lastMatch, setLastMatch] = useState(null);
    const [isScanning, setIsScanning] = useState(false);
    const scanIntervalRef = useRef(null);

    const videoConstraints = {
        width: 1280,
        height: 720,
        facingMode: "user"
    };

    // Auto-scan every 3 seconds when scanning is enabled
    useEffect(() => {
        if (isScanning) {
            scanIntervalRef.current = setInterval(() => {
                captureAndMatch();
            }, 3000);
        } else {
            if (scanIntervalRef.current) {
                clearInterval(scanIntervalRef.current);
            }
        }

        return () => {
            if (scanIntervalRef.current) {
                clearInterval(scanIntervalRef.current);
            }
        };
    }, [isScanning]);

    const captureAndMatch = async () => {
        if (isProcessing) return;

        const imageSrc = webcamRef.current?.getScreenshot();
        if (!imageSrc) {
            toast.error("Failed to capture image");
            return;
        }

        setIsProcessing(true);

        try {
            // Convert base64 to blob
            const response = await fetch(imageSrc);
            const blob = await response.blob();
            const file = new File([blob], "capture.jpg", { type: "image/jpeg" });

            // Match face
            const formData = new FormData();
            formData.append("file", file);

            const matchResponse = await api.post("/faces/match-camera", formData, {
                headers: { "Content-Type": "multipart/form-data" }
            });

            const matchData = matchResponse.data;

            if (matchData.matched && matchData.best_match) {
                const match = matchData.best_match;
                
                // Mark attendance
                const attendanceResponse = await api.post("/faces/attendance/mark", {
                    user_id: match.user_id
                });

                const attendanceData = attendanceResponse.data;

                setLastMatch({
                    name: match.user_name,
                    similarity: match.similarity,
                    timestamp: new Date().toLocaleTimeString(),
                    success: attendanceData.success,
                    message: attendanceData.message
                });

                if (attendanceData.success) {
                    toast.success(`Attendance Marked!`, {
                        description: `Welcome ${match.user_name}! Similarity: ${(match.similarity * 100).toFixed(1)}%`
                    });
                } else {
                    toast.info(attendanceData.message);
                }
            } else {
                toast.warning("No face matched", {
                    description: "Please position your face clearly in the camera"
                });
                setLastMatch(null);
            }
        } catch (error) {
            console.error("Error:", error);
            toast.error("Failed to process face", {
                description: error.response?.data?.detail || "Please try again"
            });
            setLastMatch(null);
        } finally {
            setIsProcessing(false);
        }
    };

    const toggleScanning = () => {
        setIsScanning(!isScanning);
        if (!isScanning) {
            toast.info("Auto-scanning enabled", {
                description: "Camera will check for faces every 3 seconds"
            });
        } else {
            toast.info("Auto-scanning disabled");
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-6">
            <div className="max-w-7xl mx-auto space-y-6">
                {/* Header */}
                <div className="text-center space-y-2">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent">
                        Live Attendance System
                    </h1>
                    <p className="text-muted-foreground">
                        Automatic face detection and attendance marking
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Camera Feed */}
                    <Card className="lg:col-span-2">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Camera className="h-5 w-5" />
                                Camera Feed
                            </CardTitle>
                            <CardDescription>
                                {isScanning ? "Auto-scanning enabled - checking every 3 seconds" : "Click Start Auto-Scan to begin"}
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {/* Webcam */}
                            <div className="relative rounded-lg overflow-hidden bg-black aspect-video">
                                <Webcam
                                    ref={webcamRef}
                                    audio={false}
                                    screenshotFormat="image/jpeg"
                                    videoConstraints={videoConstraints}
                                    className="w-full h-full object-cover"
                                />
                                
                                {/* Face Guide Overlay */}
                                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                                    <div className="w-64 h-80 border-4 border-blue-500/50 rounded-full shadow-lg shadow-blue-500/50">
                                        <div className="absolute -top-2 -left-2 w-8 h-8 border-t-4 border-l-4 border-blue-500 rounded-tl-lg"></div>
                                        <div className="absolute -top-2 -right-2 w-8 h-8 border-t-4 border-r-4 border-blue-500 rounded-tr-lg"></div>
                                        <div className="absolute -bottom-2 -left-2 w-8 h-8 border-b-4 border-l-4 border-blue-500 rounded-bl-lg"></div>
                                        <div className="absolute -bottom-2 -right-2 w-8 h-8 border-b-4 border-r-4 border-blue-500 rounded-br-lg"></div>
                                    </div>
                                </div>

                                {/* Scanning Indicator */}
                                {isScanning && (
                                    <div className="absolute top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium flex items-center gap-2 animate-pulse">
                                        <div className="w-2 h-2 bg-white rounded-full"></div>
                                        Scanning...
                                    </div>
                                )}

                                {/* Processing Overlay */}
                                {isProcessing && (
                                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                                        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 flex items-center gap-3">
                                            <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
                                            <span className="font-medium">Processing...</span>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Controls */}
                            <div className="flex gap-3">
                                <Button
                                    onClick={toggleScanning}
                                    className="flex-1"
                                    variant={isScanning ? "destructive" : "default"}
                                >
                                    {isScanning ? (
                                        <>
                                            <X className="h-4 w-4 mr-2" />
                                            Stop Auto-Scan
                                        </>
                                    ) : (
                                        <>
                                            <Camera className="h-4 w-4 mr-2" />
                                            Start Auto-Scan
                                        </>
                                    )}
                                </Button>
                                
                                <Button
                                    onClick={captureAndMatch}
                                    disabled={isProcessing || isScanning}
                                    variant="outline"
                                >
                                    <UserCheck className="h-4 w-4 mr-2" />
                                    Manual Check
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Status Panel */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <CheckCircle2 className="h-5 w-5" />
                                Last Match
                            </CardTitle>
                            <CardDescription>
                                Most recent attendance record
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            {lastMatch ? (
                                <div className="space-y-4">
                                    {/* Success/Already Marked Indicator */}
                                    <div className={`p-4 rounded-lg ${lastMatch.success ? 'bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800' : 'bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800'}`}>
                                        <div className="flex items-start gap-3">
                                            {lastMatch.success ? (
                                                <CheckCircle2 className="h-6 w-6 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                                            ) : (
                                                <AlertCircle className="h-6 w-6 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
                                            )}
                                            <div className="flex-1 min-w-0">
                                                <p className={`font-medium ${lastMatch.success ? 'text-green-900 dark:text-green-100' : 'text-yellow-900 dark:text-yellow-100'}`}>
                                                    {lastMatch.success ? "Attendance Marked" : "Already Marked"}
                                                </p>
                                                <p className={`text-sm mt-1 ${lastMatch.success ? 'text-green-700 dark:text-green-300' : 'text-yellow-700 dark:text-yellow-300'}`}>
                                                    {lastMatch.message}
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Match Details */}
                                    <div className="space-y-3">
                                        <div>
                                            <p className="text-sm text-muted-foreground">Employee Name</p>
                                            <p className="text-lg font-semibold">{lastMatch.name}</p>
                                        </div>
                                        
                                        <div>
                                            <p className="text-sm text-muted-foreground">Match Confidence</p>
                                            <div className="flex items-center gap-2">
                                                <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                                    <div
                                                        className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all"
                                                        style={{ width: `${lastMatch.similarity * 100}%` }}
                                                    ></div>
                                                </div>
                                                <span className="text-sm font-medium">
                                                    {(lastMatch.similarity * 100).toFixed(1)}%
                                                </span>
                                            </div>
                                        </div>
                                        
                                        <div>
                                            <p className="text-sm text-muted-foreground">Time</p>
                                            <p className="font-medium">{lastMatch.timestamp}</p>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="text-center py-8 text-muted-foreground">
                                    <UserCheck className="h-12 w-12 mx-auto mb-3 opacity-50" />
                                    <p>No matches yet</p>
                                    <p className="text-sm mt-1">Start scanning to detect faces</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
