import { useState,useRef,useCallback } from "react";
import Webcam from "react-webcam";
import {Camera,RefreshCw,CheckCircle2,AlertCircle} from 'lucide-react';
import { Button } from "@/components/ui/button";

// webcapture commponent

export default function WebcamCapture({onCapture,
    title='Capture Image',
    description="Position your fac in the frame"})
{
    //States
    const [capturedImage,setCapturedImage]=useState(null);
    const [error,setError]=useState(null);
    const [cameraReady, setCameraReady] = useState(false);
    const [loading, setLoading] = useState(true);
    

    //Refs
    const Webcamref=useRef(null);
    


    //camera start

    const capture= useCallback(async () => {
        const imageSrc=Webcamref.current.getScreenshot();

        if(!imageSrc) {
            setError('Failed to capture photo');
            return;
        }
        setCapturedImage(imageSrc);
        //base 64 to blob
        fetch(imageSrc)
        .then(res => res.blob())
        .then(blob => {
            const file= new File(
                [blob],
                `webcam-capture-${Date.now()}.jpg`,
                {type: 'image/jpeg' }
            );
            if(onCapture) {
                onCapture(file);
            }
        })
        .catch(err => {
            console.error('Capture error:',err);
            setError('Failed to process image');
        });
    }, [onCapture]);

    // retake
    const retake= () => {
        setCapturedImage(null);
        setError(null);
    };

    const handleUserMedia = () => {
        console.log("Camera ready!");
        setCameraReady(true);
        setError(null);
        setLoading(false);
    };

    const handleUserMediaError= (error) => {
        console.error('Camera error:', error);
        setCameraReady(false);
        setLoading(false);
        if (error.name === "NotAllowedError" || error.name === "PermissionDeniedError") {
            setError('Camera access denied. Please allow camera access in your browser settings and refresh the page.');
        } else if (error.name === "NotFoundError" || error.name === "DevicesNotFoundError") {
            setError('No camera found. Please connect a camera device and refresh the page.');
        } else {
            setError(`Failed to access camera: ${error.message || error.name}. Please check your camera settings.`);
        }
    };

    return (
        <div className="space-y-4">
        {/* camera view */}
        <div className="relative bg-slate-900 rounded-lg overflow-hidden aspect-video">
            {!capturedImage ? (
                <>
                <Webcam
                key="webcam-component"
                ref={Webcamref}
                audio={false}
                screenshotFormat="image/jpeg"
                screenshotQuality={0.95}
                videoConstraints= {{
                    width:1280,
                    height:720,
                    facingMode:"user",
                }}
                onUserMedia={handleUserMedia}
                onUserMediaError={handleUserMediaError}
                className="w-full h-full object-cover"
                style={{ display: error ? 'none' : 'block' }}
                />
                
                {/* Loading Indicator */}
                {loading && !error && (
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-900 text-white">
                        <div className="text-center space-y-3">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto"></div>
                            <p className="text-sm">Requesting camera access...</p>
                        </div>
                    </div>
                )}
                
                {/* Error Overlay - shown on top of camera if there's an error */}
                {error && (
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-900/95 text-white p-6">
                        <div className="text-center space-y-4 max-w-md">
                            <AlertCircle className="h-16 w-16 mx-auto text-red-500" />
                            <div>
                                <h3 className="text-lg font-semibold mb-2">Camera Access Required</h3>
                                <p className="text-sm text-gray-300">{error}</p>
                            </div>
                            <Button 
                                onClick={() => window.location.reload()} 
                                variant="outline"
                                className="mt-4"
                            >
                                <RefreshCw className="h-4 w-4 mr-2" />
                                Refresh Page
                            </Button>
                        </div>
                    </div>
                )}
                {/* face guide overlay */}
                {!error && cameraReady && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="relative">
                        {/* oval guide */}
                        <svg
                        width={280}
                        height={380}
                        viewBox="0 0 280 380"
                        className="opacity-60"
                        >
                            <ellipse
                            cx={140}
                            cy={190}
                            rx={130}
                            ry={180}
                            fill="none"
                            stroke="white"
                            strokeWidth={4}
                            strokeDasharray="10,5"
                            /> 
                        </svg>
                        <p className="absolute-bottom-10 left-1/2 transform -translate-x-0.5 text-green-400 text-sm font-medium whitespace-nowrap">
                            Position face here
                        </p>
                    </div>

                </div>
                )}
                </>
            ) : (
                // captured image preview
                <img src={capturedImage} alt="Captured" className="w-full h-full object-cover" />
            )}
        </div>

        {/* Success Message */}
                {capturedImage && (
                    <div className="bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-900 rounded-lg p-3 flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400 flex-shrink-0" />
                        <p className="text-sm text-green-800 dark:text-green-300">Photo captured successfully!</p>
                    </div>
        )}

        {/* Action buttons */}
        <div className="space-y-2">
            {!capturedImage ? (
                //Captuer button
                <Button
                onClick={capture}
                disabled={!cameraReady || error}
                className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-gray-700 hover:to-emerald-700">
                    <Camera className="h-4  w-4 mr-2"/>
                    Capture Photo
                </Button>
            ) : (
                // retake button
                <Button
                onClick={retake}
                variant="outline"
                className="w-full"
                >
                    <RefreshCw className="h-4 w-4 mr-2"/>
                    Retake Photo

                </Button>
            )}
        </div>

        {/* Tips */}
                <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900 rounded-lg p-3">
                    <h4 className="text-sm font-medium text-blue-900 dark:text-blue-400 mb-2">
                        Tips for best results:
                    </h4>
                    <ul className="text-xs text-blue-800 dark:text-blue-300 space-y-1">
                        <li>• Ensure good lighting on your face</li>
                        <li>• Look directly at the camera</li>
                        <li>• Remove glasses if possible</li>
                        <li>• Keep your face within the oval guide</li>
                    </ul>
                </div>


        </div>

    )

}