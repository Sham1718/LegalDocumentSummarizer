
import api from "../utils/axios";

export const ask=(data)=>{
    return api.post(`/api/query`, data);
}

export const getQueryHistory = (page=0,size=5) => {
  return api.get(`/api/query/history?page=${page}&size=5`, {
    params: { page, size },
  });
};