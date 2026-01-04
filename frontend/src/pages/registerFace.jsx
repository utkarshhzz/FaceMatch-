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
        if(!file.ype.startsWith('image/')) {
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
    
}