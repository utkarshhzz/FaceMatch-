import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Upload, ArrowLeft, Search, Loader2, User, AlertCircle, CheckCircle2, XCircle, Image as ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import api from "@/services/api";

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
        <div className="min-h-screen bg-gradient-to-br from-slate-50 dark:from-slate-950 to-slate-800">
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
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Search className="h-5 w-5" />
                                Match Results
                            </CardTitle>
                            <CardDescription>
                                Search results will appear here
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            {/* Loading state */}
                            {loading && (
                                <div className="text-center py-12">
                                    <Loader2 className="h-12 w-12 text-purple-600 mx-auto mb-4 animate-spin" />
                                    <p className="text-sm text-muted-foreground">
                                        Searching through registered faces...
                                    </p>
                                </div>
                            )}

                            {/* No reults abhi tak */}
                            {!loading && !matchResult && (
                                <div className="text-center py-12">
                                    <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4"/>
                                    <p className="text-muted-foreground">No results found yet</p>
                                    <p className="text-sm mt-2 text-muted-foreground">Upload a photo and click "Find Match"</p>
                                </div>
                            )}

                            {/* Match Found */}
                            {!loading && matchResult && matchResult.match_found && (
                                <div className="space-y-4">
                                    {/* Success banner */}
                                    <div className="bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-900 rounded-lg p-4">
                                        <div className="flex items-center gap-2 mb-2">
                                            <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                                            <h3 className="font-semibold text-green-900 dark:text-green-400">
                                                Match Found!
                                            </h3>
                                        </div>
                                        <p className="text-sm text-green-800 dark:text-green-300 ">
                                            We found a matching face in database

                                        </p>

                                    </div>

                                    {/* Person info */}
                                    <div className="border rounded-lg p-4">
                                        <div className="flex items-center gap-3 mb-3">
                                            <div className="h-12 w-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
                                                <User className="h-6 w-6 text-white"/>
                                            </div>
                                            <div>
                                                <h3 className="font-semibold text-lg">
                                                    {matchResult.person_name}
                                                </h3>
                                                <p className="text-xs text-muted-foreground">
                                                    Registered Person
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Confidence Score */}
                                    <div className="space-y-2">
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm font-medium">Confidence Score</span>
                                            <span className={`text-sm font-bold ${getConfidenceColor(matchResult.confidence)}`}>
                                                {(matchResult.confidence *100).toFixed(1)}%
                                            </span>
                                        </div>
                                        {/* Progress Bar */}
                                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded full h-2">
                                            <div className="bg-gradient-to-r from-purple-600 to-pink-600 h-2 rounded-full transition-all"
                                            style={{width: `${matchResult.confidence * 100}%`}}></div>
                                        </div>
                                        {/* Confidence Badge */}
                                            <div className="flex justify-center">
                                                <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getConfidenceBadge(matchResult.confidence)}`}>
                                                    {matchResult.confidence >= 0.8 ? 'High Confidence' : 
                                                     matchResult.confidence >= 0.6 ? 'Medium Confidence' : 
                                                     'Low Confidence'}
                                                </span>
                                            </div>
                                    </div>
                                    {/* Additional Info */}
                                        <div className="mt-4 pt-4 border-t">
                                            <p className="text-xs text-muted-foreground">
                                                <AlertCircle className="inline h-3 w-3 mr-1" />
                                                Match confidence indicates how certain we are about this match
                                            </p>
                                        </div>
                                    
                                        


                                    
                                    
                                </div>
                            )}   

                            {/* No match found */}
                            {!loading && matchResult && !matchResult.match_found && (
                                <div className="space-y-4">
                                    {/* No match banner */}
                                    <div className="bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 dark:border-yellow-900 rounded-lg p-4">
                                    <div className="flex items-center gap-2 mb-2">
                                        <XCircle  className="h-5 w-5 text-yellow-600 dark:text-yellow-400"/>
                                        <h3 className="font-semibold text-yellow-900 dark:text-yellow-400">
                                            No Match Found
                                        </h3>
                                    </div>
                                    <p className="text-sm text-yellow-800 dark:text-yellow-300">
                                        This face is not registered in our database...
                                    </p>
                                    </div> 

                                    {/* Suggestions */}
                                    <div className="border rounded-lg p-4">
                                        <h4 className="font-medium mb-3">
                                            What you can try...
                                        </h4>
                                        <div className="space-y-2">
                                            <Button
                                            variant="outline"
                                            className="w-full justify-start"
                                            onClick={() => navigate('/register-face')}
                                            >
                                                <Upload className="h-4 w-4 mr-2"/>
                                                Register this person
                                            </Button>
                                            <Button
                                            variant="outline"
                                            className="w-full justify-start"
                                            onClick={handleClear}
                                            >
                                                Try another photo
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                </div>
            </div>
            
        
        
        
        </div>
    )
}