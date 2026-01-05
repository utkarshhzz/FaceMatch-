import { useState,useRef,useCallback } from "react";
import Webcam from "react-webcam";
import {Camera,X,RefreshCw,CheckCircle2,AlertCircle} from 'lucide-react';
import { Button } from "@/components/ui/button";
import {Card,CardContent,CardHeader,CardTitle,CardDescription} from "@/components/ui/card";

// webcapture commponent

export default function WebcamCapture({onCapture,
    title='Capture Image',
    description="Position your fac in the frame"})
{
    //States
    const [capturedImage,setCapturedImage]=useState(null);
    const [error,setError]=useState(null);
    

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

    const handleUserMediaError= (error) => {
        console.error('Camera error:', error);
        setError('Camera access denied.please enable camera permissions...');
    };

    return (
        <Card>
        <CardHeader>
            <CardTitle className="flex items-center gap-2">
                <Camera className="h-5 w-5"/>
                {title}

            </CardTitle>
            <CardDescription> {description}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4"> 
        {/* camera view */}
        <div className="relative bg-slate-900 rounded-lg overflow-hidden aspect-video">
            {!capturedImage ? (
                <>
                <Webcam
                ref={Webcamref}
                audio={false}
                screenshotFormat="image/jpeg"
                screenshotQuality={0.95}
                videoConstraints= {{
                    width:1200,
                    height:720,
                    facingMode:"user",
                }}
                onUserMediaError={handleUserMediaError}
                className="w-full h-full object-cover"
                />
                {/* face guide overlay */}
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
                </>
            ) : (
                // captured image preview
                <img src={capturedImage} alt="Captured" className="w-full h-full object-cover" />
            )}
        </div>
        {error && (
            <div className="bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900 rounded-lg p-3 flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400 flex-shrink-0"/>
                <p className="text-sm text-red-800 dark:text-red-300">{error}</p>
            </div>
        )}

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


        </CardContent>
        </Card>

    )

}