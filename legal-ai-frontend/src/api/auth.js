import api from '../utils/axios'

export const loginUser=(data)=>{
    return api.post("/auth/login",data)
}

export const register=(data)=>{
    return api.post(`/auth/register`,data)
}