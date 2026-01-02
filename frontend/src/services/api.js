import axios from 'axios';

//Base API URL (backend server)
const API_URL='http://localhost:8000/api/v1';

//create axios instance with default config
const api=axios.create({
    baseURL:API_URL,
    headers: {
        'Content-Type':'application/json',
    },
});

//token ko request mein automatically add krenge
api.interceptors.request.use((config) => {
    const token=localStorage.getItem('token');
    if(token) {
        config.headers.Authorization=`Bearer ${token}`;
    }
    return config;
});

//Authentication API's
export const authAPI={
    register:(data)=> api.post('/auth/register',data),
    login:(data)=> api.post('/auth/login',data),
    getCurrentUser:()=>api.get('/auth/me'),
}



//Face api's
export const faceAPI= {
    registerFace: (formdata)=> api.post('/faces/register',formdata,{
        headers: { 'Content-Type':'multipart/form-data'},
    }),

    matchFace: (formdata) => api.post('/faces/match',formdata, {
        headers: {'Content-Type': 'multipart/form-data'},
    }),
    getMyFaces: () => api.get('/faces/my-faces'),
    deleteFace: (faceId)=> api.delete(`/faces/${faceId}`),
};

export default api;