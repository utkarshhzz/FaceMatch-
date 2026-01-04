import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Upload, ArrowLeft, User, Loader2, CheckCircle2, Image as ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import api from "@/services/api";


export default function RegisterFace() {
    //State variables 
    const [personName,setPersonName]=useState('');
    const [selectedImage,setSelectedImage]=useState(null);
    const [previewUrl,setPreviewUrl]=useState(null);
    const [loading,setLoading]=useState(false);
    const {user}= useAuth();
    const navigate=useNavigate();

    //Handling image
    const handleImageSelect=(e) => {
        const file=e.target.files[0];

        if(!file) return;
        //Validation
        if(!file.type.startsWith('image/')) {
            toast.error('Please select an image file');
            return;
        }

        //Size validatipm
        if(file.size>5*1024*1024) {
            toast.error('Image size should be less than 5MB');
            return;

        }
        setSelectedImage(file);
        //Creating preview url
        const reader=new FileReader();
        reader.onloadend=() => {
            setPreviewUrl(reader.result);
        };
        reader.readAsDataURL(file);
    };

    //Form submission Hanler
    const handleSubmit= async (e) => {
        e.preventDefault();

        if(!selectedImage) {
            toast.error('Please selec an Image');
            return;
        }
        if(!personName.trim()) {
            toast.error('Please enter Person Name');
            return;
        }

        setLoading(true);

        try {
            //Creating formdata to senf files
            const formdata= new FormData();
            formdata.append('image',selectedImage);
            formdata.append('person_name',personName);

            //sending to backend
            const response=await api.post('/faces/register',formdata, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            toast.success('Face Registered Successfully', {
                description:`${personName}'s face has been registered.`,
            });

            //reset the form
            setPersonName('');
            setSelectedImage(null);
            setPreviewUrl(null);

            //eredirect ti dashboard ater 2 seconds
            setTimeout(() => {
                navigate('/dashboard');
            },2000);
        } catch(error) {
            console.error('Registration failed',error);
            toast.error('Failed to register face', {
                description:error.response?.data?.message || 'Please try again.',
            });
        } finally {
            setLoading(false);
        }
    };

    //clear selection
    const handleClear= () => {
        setSelectedImage(null);
        setPreviewUrl(null);
        setPersonName('');
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 to-slate-900">
            {/* Header */}
            <div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <Button
                    variant="ghost"
                    onClick={() => navigate('/dashboard')}
                    className="mb-4"
                    >
                    <ArrowLeft className="h-4 w-4 mr-2">Back to Dashboard</ArrowLeft>
                    </Button>

                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Register New Face</h1>
                    <p className="text-slate-600 dark:text-slate-400 mt-2">Upload a photo and register a new face to the database</p>
                </div>
            </div>

            {/* MAin Content */}
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <form onSubmit={handleSubmit}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                    {/* left side image uplaoder  */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <ImageIcon className="h-5 w-5"/>
                                Upload Photo
                            </CardTitle>
                            <CardDescription>
                                Select a clear photo with visible face
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">

                            {/* Preview area */}
                            <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-lg p-6 text-center">
                                {previewUrl? (
                                    <div className="space-y-4">
                                        <img src="{previewUrl}" alt="Preview" className="max-h-64 mx-auto roundedd-lg" />
                                        <p className="text-sm text-muted-foreground">{selectedImage?.name}
                                             </p>
                                    </div>
                                ):(
                                    <div className="py-12">
                                        <Upload className="h-12 w-12 mx-auto text-muted-foreground mb-4"/>
                                        <p className="text-sm text-muted-foreground mb-2">Click to upload or drag and drop

                                        </p>
                                        <p className="text-xs text-muted-foreground">PNG,JPG upto 5mb

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

                            {previewUrl && (
                                <Button
                                type="button"
                                variant="outline"
                                onClick={handleClear}
                                className="w-full"
                                >
                                    Clear Selection
                                </Button>
                            )}
                            

                        </CardContent>
                    </Card>

                    {/* right side person details */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <User className="h-5 w-5"/>
                                Person Details
                            </CardTitle>
                            <CardDescription>
                                Enter information about the person
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {/* person name input  */}
                            <div className="space-y-2">
                                <Label htmlFor="fullname">Full Name</Label>
                                <Input
                                    id="personName"
                                    type="text"
                                    placeholder="Utkarsh Kumar"
                                    value={personName}
                                    onChange={(e) => setPersonName(e.target.value)}
                                    required                       
                                />
                                <p className="text-xs text-muted-foreground">Enter full name of person in the photo</p>
                            </div>
                            
                            {/* info card */}
                            <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900 rounded-lg p-4">
                            <h4 className="text-sm font-medium text-blue-900 dark:text-blue-400 mb-2">Tips for best results</h4>
                            <ul className="text-xs text-blue-800 dark:text-blue-300 space-y-1">
                                <li>• Use a clear, well-lit photo</li>
                                <li>• Face should be clearly visible</li>
                                <li>• Avoid sunglasses or face coverings</li>
                                <li>• Front-facing photos work best</li>

                            </ul>
                            </div>


                        </CardContent>
                        <CardFooter className="flex flex-col gap-3">
                            <Button
                            type="submit"
                            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
                            disabled={loading|| !selectedImage || !personName}

                            >
                               {loading? (
                                <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Registering...
                                </>
                               ): (
                                <>
                                <CheckCircle2 className="mr-2 h-4 w-4"/>
                                Register Face
                                </>
                               )} 
                                
                            </Button>

                            <Button
                            type="button"
                            variant="outline"
                            onClick={()=> navigate('/dashboard')}
                            className="w-full"
                            disabled={loading}>
                                Cancel
                            </Button>

                        </CardFooter>
                    </Card>

                </div>
                </form>

            </div>

        </div>
    )


}
    

