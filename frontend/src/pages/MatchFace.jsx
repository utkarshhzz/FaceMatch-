import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Upload, ArrowLeft, Search, Loader2, User, AlertCircle, CheckCircle2, XCircle, Image as ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import api from "@/services/api";
import { preview } from "vite";

export default function MatchFace() {
    //state variables
    const [selectedImage,setSelectedImage]= useState(null);
    const [previewUrl,setPreviewUrl]= useState(null);
    const [loading,setLoading]= useState(false);
    const [matchResult,setMatchResult]= useState(null);

    const {user} =useAuth();
    const navigate=useNavigate();

    const handleImageSelect= (e) => {
        const file=e.target.files[0];

        if(!file) return;
        if(!file.type.startsWith('image/')) {
            toast.error('Please select an image file...');
            return;
        }

        //Size validation
        if(file.size > 5*1024*1024) {
            toast.error('File size exceeds 5MB limit.');
            return;
        };
        setSelectedImage(file);
        setMatchResult(null); //clearing prev rsults

        //preview URl
        const reader= new FileReader();
        reader.onloadend= () => {
            setPreviewUrl(reader.result);
        };
        reader.readAsDataURL(file);
    };

    //Hnadle face matching
    const handleMatch=async () => {
        if(!selectedImage) {
            toast.error('Please select an image frist...');
            return;
        }
        setLoading(true);
        setMatchResult(null);

        try {
            //crearing form data
            const formdata= new FormData();
            formdata.append('image',selectedImage);

            //sending image to backend
            const response = await api.post('/faces/match',formdata, {
                headers: {
                    'Content-Type':'multipart/form-data',
                },
            });

            setMatchResult(response.data);

            if(response.data.match_found) {
                toast.success('Match found!', {
                    description: `Matched with ${response.data.person_name}`,
                });
            } else {
                toast.info("No match found.", {
                    description: "This face is not in the database",
                });
            }
        } catch (error) {
            toast.error("An error occurred while matching the face.");
        } finally {
            setLoading(false);
        }
    };

    //Clearing selection
    const handleClear= () => {
        setSelectedImage(null);
        setPreviewUrl(null);
        setMatchResult(null);
    };

    //confidence metrics]

    const getConfidenceColor= (confidence) => {
        if(confidence >=0.8) return 'text-green-600 dark: text-green-400';
        if(confidence >=0.6) return 'text-yellow-600 dark: text-yellow-400';
        return 'text-red-600 dark:text-red-400';

    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 to-slate-800">
            {/* header */}
            <div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <Button
                    variant="ghost"
                    onClick={() => navigate('/dashboard')}
                    className="mb-4"
                    >
                        <ArrowLeft className="h-4 w-4 mr-2"/>
                        Back to Dashboard
                    </Button>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                        Match Face
                    </h1>
                    <p className="text-slate-600 dark:text-slate-400 mt-2">
                        Upload a photo to find matching faces in database...
                        </p>
                </div>

            </div>

            {/* Main content */}
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* left side image uplaod */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <ImageIcon className="h-5 w-5"/>
                                Upload photo to Match

                            </CardTitle>
                            <CardDescription>
                                Select a photo with a face to search
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {/* preview area */}
                            <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-lg p-6 text-center">
                                {previewUrl? (
                                    <div className="space-y-4">
                                        <img src="{previewUrl}" alt="Preview" className="max-h-64 mx-auto rounded-lg" />
                                        <p className="text-sm text-muted-foreground">
                                            {selectedImage?.name}
                                        </p>

                                    </div>
                                ): (
                                    <div className="py-12">
                                        <Upload className="h-12 w-12 mx-auto text-muted-foreground mb-4"/>
                                        <p className="text-sm text-muted-foreground mb-2">
                                            Click to upload or drag and drop
                                            </p>
                                        <p className="text-xs text-muted-foreground">
                                            PNG,JPG upto 5MB
                                        </p>

                                    </div>

                                )}

                            </div>

                            {/* File input */}
                            <Input
                            type="file"
                            accept="image/*"
                            onChange={handleImageSelect}
                            className="cursor-pointer"
                            />

                            {/* Action Buttons */}
                            <div className="space-y-2">
                                <Button
                                onClick={handleMatch}
                                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                                disabled={loading || !selectedImage}
                                >
                                    {loading ? (
                                        <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin"/>
                                        Matching
                                        </>
                                    ): (
                                        <>
                                        <Search className="mr-2 h-4 w-4" />
                                        Match Face
                                        </>
                                    )}


                                
                                </Button>

                                {previewUrl && (
                                    <Button
                                    type="button"
                                    variant="outline"
                                    onClick={handleClear}
                                    className="w-full"
                                    
                                    >
                                        Clear and Try Again

                                    </Button>
                                )}

                            </div>
                            {/* Tips Card */}
                            <div className="bg-purple-50 dark:bg-purple-950/20 border border-purple-200 dark:border-purple-900 rounded-lg p-4">
                                <h4 className="text-sm font-medium text-purple-900 dark:text-purple-400 mb-2">
                                    Tips for best results:
                                </h4>
                                <ul className="text-xs text-purple-800 dark:text-purple-300 space-y-1">
                                    <li>• Use a clear, well-lit photo</li>
                                    <li>• Face should be clearly visible</li>
                                    <li>• Avoid heavy filters or edits</li>
                                    <li>• Front-facing photos work best</li>
                                </ul>
                            </div>


                        </CardContent>
                    </Card>

                    {/* Right Side Match Results */}
                    <Card>
                        
                    </Card>

                </div>
            </div>
            
        
        
        
        </div>
    )
}