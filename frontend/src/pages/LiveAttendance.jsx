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
    const [cameraError, setCameraError] = useState(null);
    const scanIntervalRef = useRef(null);

    const videoConstraints = {
        width: 1280,
        height: 720,
        facingMode: "user"
    };

    const handleUserMediaError = (error) => {
        console.error("Camera error:", error);
        if (error.name === "NotAllowedError" || error.name === "PermissionDeniedError") {
            setCameraError("Camera access denied. Please allow camera access in your browser settings.");
            toast.error("Camera Access Denied", {
                description: "Please allow camera access and refresh the page"
            });
        } else if (error.name === "NotFoundError" || error.name === "DevicesNotFoundError") {
            setCameraError("No camera found. Please connect a camera device.");
            toast.error("No Camera Found");
        } else {
            setCameraError("Failed to access camera. Please check your camera settings.");
            toast.error("Camera Error", {
                description: error.message || "Unknown error"
            });
        }
    };

    const handleUserMedia = () => {
        setCameraError(null);
        toast.success("Camera ready", {
            description: "You can now start scanning for attendance"
        });
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

            console.log("Captured file:", file.name, file.size, file.type);

            // Match face
            const formData = new FormData();
            formData.append("file", file);

            console.log("Sending match request...");
            const matchResponse = await api.post("/faces/match-camera", formData, {
                headers: { "Content-Type": "multipart/form-data" }
            });

            console.log("Match response:", matchResponse.data);
            const matchData = matchResponse.data;

            if (matchData.matched && matchData.best_match) {
                const match = matchData.best_match;
                
                console.log("Face matched! Marking attendance for user:", match.user_id);
                
                // Mark attendance
                const attendanceResponse = await api.post("/faces/attendance/mark", {
                    user_id: match.user_id
                });

                console.log("Attendance response:", attendanceResponse.data);
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
                console.log("No face matched. Response:", matchData);
                toast.warning("No face matched", {
                    description: "Please position your face clearly in the camera"
                });
                setLastMatch(null);
            }
        } catch (error) {
            console.error("Error details:", error);
            console.error("Error response:", error.response?.data);
            console.error("Error status:", error.response?.status);
            
            const errorDetail = error.response?.data?.detail || error.message;
            
            // Handle specific error cases
            if (errorDetail?.includes("No face detected")) {
                // Only show toast for manual captures, not auto-scan
                if (!isScanning) {
                    toast.warning("No face detected", {
                        description: "Make sure your face is visible, centered, and well-lit"
                    });
                }
                setLastMatch(null);
            } else {
                toast.error("Failed to process face", {
                    description: errorDetail || "Please try again"
                });
                setLastMatch(null);
            }
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
                                {cameraError ? (
                                    <div className="absolute inset-0 flex items-center justify-center bg-gray-900 text-white p-6">
                                        <div className="text-center space-y-4">
                                            <AlertCircle className="h-16 w-16 mx-auto text-red-500" />
                                            <div>
                                                <h3 className="text-lg font-semibold mb-2">Camera Access Required</h3>
                                                <p className="text-sm text-gray-300 max-w-md mx-auto">{cameraError}</p>
                                            </div>
                                            <div className="space-y-2 text-xs text-left bg-gray-800 p-4 rounded-lg max-w-md mx-auto">
                                                <p className="font-semibold text-white">To enable camera:</p>
                                                <ol className="list-decimal list-inside space-y-1 text-gray-300">
                                                    <li>Click the camera icon in your browser's address bar</li>
                                                    <li>Select "Allow" for camera access</li>
                                                    <li>Refresh this page</li>
                                                </ol>
                                            </div>
                                            <Button 
                                                onClick={() => window.location.reload()} 
                                                variant="outline"
                                                className="mt-4"
                                            >
                                                Refresh Page
                                            </Button>
                                        </div>
                                    </div>
                                ) : (
                                    <Webcam
                                        ref={webcamRef}
                                        audio={false}
                                        screenshotFormat="image/jpeg"
                                        videoConstraints={videoConstraints}
                                        className="w-full h-full object-cover"
                                        onUserMedia={handleUserMedia}
                                        onUserMediaError={handleUserMediaError}
                                    />
                                )}
                                
                                {/* Face Guide Overlay */}
                                {!cameraError && (
                                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                                        <div className="w-64 h-80 border-4 border-blue-500/50 rounded-full shadow-lg shadow-blue-500/50">
                                            <div className="absolute -top-2 -left-2 w-8 h-8 border-t-4 border-l-4 border-blue-500 rounded-tl-lg"></div>
                                            <div className="absolute -top-2 -right-2 w-8 h-8 border-t-4 border-r-4 border-blue-500 rounded-tr-lg"></div>
                                            <div className="absolute -bottom-2 -left-2 w-8 h-8 border-b-4 border-l-4 border-blue-500 rounded-bl-lg"></div>
                                            <div className="absolute -bottom-2 -right-2 w-8 h-8 border-b-4 border-r-4 border-blue-500 rounded-br-lg"></div>
                                        </div>
                                    </div>
                                )}

                                {/* Scanning Indicator */}
                                {isScanning && !cameraError && (
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
                                    disabled={!!cameraError}
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
                                    disabled={isProcessing || isScanning || !!cameraError}
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

                {/* Tips Card */}
                <Card className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
                    <CardHeader>
                        <CardTitle className="text-blue-900 dark:text-blue-100 flex items-center gap-2">
                            <AlertCircle className="h-5 w-5" />
                            Tips for Best Results
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-2 text-sm text-blue-800 dark:text-blue-200">
                            <li className="flex items-start gap-2">
                                <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                                <span>Position your face within the oval guide</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                                <span>Ensure good lighting on your face</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                                <span>Look directly at the camera</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                                <span>Stay still when scanning</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                                <span>Make sure your full face is visible (no masks or hats)</span>
                            </li>
                        </ul>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
