import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Camera, Upload, CheckCircle, XCircle, ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import api from "@/services/api";

export default function RegisterMultipleFaces() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        employee_id: "",
        full_name: "",
        email: ""
    });
    
    const [photos, setPhotos] = useState({
        photo1: { file: null, preview: null, uploaded: false },
        photo2: { file: null, preview: null, uploaded: false },
        photo3: { file: null, preview: null, uploaded: false }
    });
    
    const [uploading, setUploading] = useState(false);

    // Handle form input changes
    const handleInputChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    // Handle photo selection
    const handlePhotoSelect = (photoNumber, file) => {
        if (!file) return;

        const reader = new FileReader();
        reader.onloadend = () => {
            setPhotos({
                ...photos,
                [`photo${photoNumber}`]: {
                    file: file,
                    preview: reader.result,
                    uploaded: false
                }
            });
        };
        reader.readAsDataURL(file);
    };

    // Upload single photo
    const uploadPhoto = async (photoNumber) => {
        const photo = photos[`photo${photoNumber}`];
        
        if (!photo.file) {
            toast.error(`Please select photo ${photoNumber} first`);
            return;
        }

        // Validate form data for first photo
        if (photoNumber === 1) {
            if (!formData.employee_id || !formData.full_name || !formData.email) {
                toast.error("Please fill in all details first");
                return;
            }
        }

        setUploading(true);

        try {
            const formDataToSend = new FormData();
            formDataToSend.append('file', photo.file);
            formDataToSend.append('employee_id', formData.employee_id);
            formDataToSend.append('full_name', formData.full_name);
            formDataToSend.append('email', formData.email);
            formDataToSend.append('photo_number', photoNumber);

            const response = await api.post('/faces/register', formDataToSend, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            toast.success(response.data.message);
            
            // Mark as uploaded
            setPhotos({
                ...photos,
                [`photo${photoNumber}`]: {
                    ...photo,
                    uploaded: true
                }
            });

        } catch (error) {
            console.error('Upload error:', error);
            toast.error(error.response?.data?.detail || 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    // Upload all photos at once
    const uploadAllPhotos = async () => {
        // Upload in sequence: 1, 2, 3
        for (let i = 1; i <= 3; i++) {
            if (photos[`photo${i}`].file && !photos[`photo${i}`].uploaded) {
                await uploadPhoto(i);
            }
        }

        toast.success("All photos uploaded successfully!");
        
        // Navigate back after 2 seconds
        setTimeout(() => {
            navigate('/admin-dashboard');
        }, 2000);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-950 dark:to-slate-900 p-6">
            <div className="max-w-5xl mx-auto">
                
                {/* Header */}
                <div className="flex items-center gap-4 mb-6">
                    <Button
                        variant="outline"
                        onClick={() => navigate('/admin-dashboard')}
                    >
                        <ArrowLeft className="h-4 w-4 mr-2" />
                        Back
                    </Button>
                    <div>
                        <h1 className="text-3xl font-bold">Register Multiple Face Photos</h1>
                        <p className="text-muted-foreground">
                            Upload 2-3 photos for better accuracy (front, left, right angles)
                        </p>
                    </div>
                </div>

                {/* Employee Details Form */}
                <Card className="mb-6">
                    <CardHeader>
                        <CardTitle>Employee Details</CardTitle>
                        <CardDescription>
                            Fill in once, then upload multiple photos
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <Label>Employee ID</Label>
                            <Input
                                name="employee_id"
                                value={formData.employee_id}
                                onChange={handleInputChange}
                                placeholder="123456"
                            />
                        </div>
                        <div>
                            <Label>Full Name</Label>
                            <Input
                                name="full_name"
                                value={formData.full_name}
                                onChange={handleInputChange}
                                placeholder="John Doe"
                            />
                        </div>
                        <div>
                            <Label>Email</Label>
                            <Input
                                name="email"
                                type="email"
                                value={formData.email}
                                onChange={handleInputChange}
                                placeholder="john@company.com"
                            />
                        </div>
                    </CardContent>
                </Card>

                {/* Photo Upload Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                    
                    {/* Photo 1: Front */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center justify-between">
                                Photo 1: Front View
                                {photos.photo1.uploaded && (
                                    <CheckCircle className="h-5 w-5 text-green-600" />
                                )}
                            </CardTitle>
                            <CardDescription>
                                Look straight at camera
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {photos.photo1.preview ? (
                                <img
                                    src={photos.photo1.preview}
                                    alt="Photo 1"
                                    className="w-full h-64 object-cover rounded-lg"
                                />
                            ) : (
                                <div className="w-full h-64 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center">
                                    <Camera className="h-16 w-16 text-slate-400" />
                                </div>
                            )}
                            
                            <input
                                type="file"
                                id="photo1-input"
                                accept="image/*"
                                onChange={(e) => handlePhotoSelect(1, e.target.files[0])}
                                className="hidden"
                            />
                            
                            <div className="flex gap-2">
                                <Button
                                    variant="outline"
                                    className="flex-1"
                                    onClick={() => document.getElementById('photo1-input').click()}
                                    disabled={photos.photo1.uploaded}
                                >
                                    <Upload className="h-4 w-4 mr-2" />
                                    Select
                                </Button>
                                <Button
                                    className="flex-1"
                                    onClick={() => uploadPhoto(1)}
                                    disabled={!photos.photo1.file || photos.photo1.uploaded || uploading}
                                >
                                    Upload
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Photo 2: Left */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center justify-between">
                                Photo 2: Left Angle
                                {photos.photo2.uploaded && (
                                    <CheckCircle className="h-5 w-5 text-green-600" />
                                )}
                            </CardTitle>
                            <CardDescription>
                                Turn face slightly left
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {photos.photo2.preview ? (
                                <img
                                    src={photos.photo2.preview}
                                    alt="Photo 2"
                                    className="w-full h-64 object-cover rounded-lg"
                                />
                            ) : (
                                <div className="w-full h-64 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center">
                                    <Camera className="h-16 w-16 text-slate-400" />
                                </div>
                            )}
                            
                            <input
                                type="file"
                                id="photo2-input"
                                accept="image/*"
                                onChange={(e) => handlePhotoSelect(2, e.target.files[0])}
                                className="hidden"
                            />
                            
                            <div className="flex gap-2">
                                <Button
                                    variant="outline"
                                    className="flex-1"
                                    onClick={() => document.getElementById('photo2-input').click()}
                                    disabled={!photos.photo1.uploaded || photos.photo2.uploaded}
                                >
                                    <Upload className="h-4 w-4 mr-2" />
                                    Select
                                </Button>
                                <Button
                                    className="flex-1"
                                    onClick={() => uploadPhoto(2)}
                                    disabled={!photos.photo2.file || !photos.photo1.uploaded || photos.photo2.uploaded || uploading}
                                >
                                    Upload
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Photo 3: Right */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center justify-between">
                                Photo 3: Right Angle
                                {photos.photo3.uploaded && (
                                    <CheckCircle className="h-5 w-5 text-green-600" />
                                )}
                            </CardTitle>
                            <CardDescription>
                                Turn face slightly right
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {photos.photo3.preview ? (
                                <img
                                    src={photos.photo3.preview}
                                    alt="Photo 3"
                                    className="w-full h-64 object-cover rounded-lg"
                                />
                            ) : (
                                <div className="w-full h-64 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center">
                                    <Camera className="h-16 w-16 text-slate-400" />
                                </div>
                            )}
                            
                            <input
                                type="file"
                                id="photo3-input"
                                accept="image/*"
                                onChange={(e) => handlePhotoSelect(3, e.target.files[0])}
                                className="hidden"
                            />
                            
                            <div className="flex gap-2">
                                <Button
                                    variant="outline"
                                    className="flex-1"
                                    onClick={() => document.getElementById('photo3-input').click()}
                                    disabled={!photos.photo1.uploaded || photos.photo3.uploaded}
                                >
                                    <Upload className="h-4 w-4 mr-2" />
                                    Select
                                </Button>
                                <Button
                                    className="flex-1"
                                    onClick={() => uploadPhoto(3)}
                                    disabled={!photos.photo3.file || !photos.photo1.uploaded || photos.photo3.uploaded || uploading}
                                >
                                    Upload
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                </div>

                {/* Upload All Button */}
                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className="font-semibold mb-1">Ready to submit?</h3>
                                <p className="text-sm text-muted-foreground">
                                    Upload all selected photos at once
                                </p>
                            </div>
                            <Button
                                size="lg"
                                onClick={uploadAllPhotos}
                                disabled={!photos.photo1.file || uploading}
                            >
                                {uploading ? "Uploading..." : "Upload All Photos"}
                            </Button>
                        </div>
                    </CardContent>
                </Card>

            </div>
        </div>
    );
}