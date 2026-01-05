import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Upload, ArrowLeft, User, Loader2, CheckCircle2, Image as ImageIcon, Camera } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import api from "@/services/api";
import WebcamCapture from "@/components/WebcamCapture";


export default function RegisterFace() {
    //State variables 
    const [selectedImage,setSelectedImage]=useState(null);
    const [previewUrl,setPreviewUrl]=useState(null);
    const [loading,setLoading]=useState(false);
    const [employeeId, setEmployeeId] = useState('');
    const [fullName, setFullName] = useState('');
    const {user}= useAuth();
    const navigate=useNavigate();
    const [captureMode,setCaptureMode]=useState('upload'); //upload or camera

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
            toast.error('Please select an image');
            return;
        }

        if(!employeeId.trim()) {
            toast.error('Please enter employee ID');
            return;
        }

        if(!fullName.trim()) {
            toast.error('Please enter full name');
            return;
        }

        setLoading(true);

        try {
            //Creating formdata to send files
            const formdata= new FormData();
            formdata.append('file',selectedImage);
            formdata.append('employee_id', employeeId.trim());
            formdata.append('full_name', fullName.trim());

            //sending to backend
            const response=await api.post('/faces/register',formdata, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            toast.success('Face Registered Successfully', {
                description:`Employee ${fullName} (ID: ${employeeId}) has been registered.`,
            });

            //reset the form
            setSelectedImage(null);
            setPreviewUrl(null);
            setEmployeeId('');
            setFullName('');

            //eredirect ti dashboard ater 2 seconds
            setTimeout(() => {
                navigate('/dashboard');
            },2000);
        } catch(error) {
            console.error('Registration failed', error);
            console.error('Error response:', error.response?.data);
            console.error('Error status:', error.response?.status);
            
            const errorMessage = error.response?.data?.detail || error.message || 'Please try again.';
            
            toast.error('Failed to register face', {
                description: errorMessage,
                duration: 5000,
            });
        } finally {
            setLoading(false);
        }
    };

    //clear selection
    const handleClear= () => {
        setSelectedImage(null);
        setPreviewUrl(null);
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

                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Register Your Face</h1>
                    <p className="text-slate-600 dark:text-slate-400 mt-2">Upload your photo to register your face</p>
                </div>
            </div>

            {/* MAin Content */}
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <form onSubmit={handleSubmit}>
                
                {/* Employee Details Section */}
                <Card className="mb-6">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <User className="h-5 w-5"/>
                            Employee Details
                        </CardTitle>
                        <CardDescription>
                            Enter employee information
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="employeeId">Employee ID *</Label>
                                <Input
                                    id="employeeId"
                                    type="text"
                                    placeholder="Enter employee ID"
                                    value={employeeId}
                                    onChange={(e) => setEmployeeId(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="fullName">Full Name *</Label>
                                <Input
                                    id="fullName"
                                    type="text"
                                    placeholder="Enter full name"
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    required
                                />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                    {/* left side image uplaoder  */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <ImageIcon className="h-5 w-5"/>
                                Add Your Photo
                            </CardTitle>
                            <CardDescription>
                                Choose how to add your face photo
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">

                            {/* Mode Toggle Buttons */}
                            <div className="flex gap-2 p-1 bg-slate-100 dark:bg-slate-800 rounded-lg">
                                <Button
                                    type="button"
                                    variant={captureMode === 'upload' ? 'default' : 'ghost'}
                                    className="flex-1"
                                    onClick={() => {
                                        setCaptureMode('upload');
                                        handleClear();
                                    }}
                                >
                                    <Upload className="h-4 w-4 mr-2" />
                                    Upload File
                                </Button>
                                <Button
                                    type="button"
                                    variant={captureMode === 'camera' ? 'default' : 'ghost'}
                                    className="flex-1"
                                    onClick={() => {
                                        setCaptureMode('camera');
                                        handleClear();
                                    }}
                                >
                                    <Camera className="h-4 w-4 mr-2" />
                                    Use Camera
                                </Button>
                            </div>

                            {/* Upload Mode */}
                            {captureMode === 'upload' && (
                            <>
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
                            </>
                            )}

                            {/* Camera Mode */}
                            {captureMode === 'camera' && (
                                <WebcamCapture
                                    onCapture={(file) => {
                                        console.log('Camera captured file:', file);
                                        setSelectedImage(file);
                                        const url = URL.createObjectURL(file);
                                        setPreviewUrl(url);
                                        console.log('States updated - selectedImage:', file.name, 'previewUrl:', url);
                                    }}
                                    title="Capture Your Face"
                                    description="Position your face in the oval and click capture"
                                />
                            )}

                        </CardContent>
                    </Card>

                    {/* right side tips */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <CheckCircle2 className="h-5 w-5"/>
                                Tips for Best Results
                            </CardTitle>
                            <CardDescription>
                                Follow these guidelines for accurate face registration
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {/* info card */}
                            <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900 rounded-lg p-4">
                            <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-2">
                                <li className="flex items-start gap-2">
                                    <span className="text-blue-600 dark:text-blue-400">✓</span>
                                    <span>Use a clear, well-lit photo</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-blue-600 dark:text-blue-400">✓</span>
                                    <span>Face should be clearly visible</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-blue-600 dark:text-blue-400">✓</span>
                                    <span>Avoid sunglasses or face coverings</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-blue-600 dark:text-blue-400">✓</span>
                                    <span>Front-facing photos work best</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-blue-600 dark:text-blue-400">✓</span>
                                    <span>Neutral expression recommended</span>
                                </li>
                            </ul>
                            </div>


                        </CardContent>
                        <CardFooter className="flex flex-col gap-3">
                            <Button
                            type="submit"
                            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
                            disabled={loading|| !selectedImage}

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
    

