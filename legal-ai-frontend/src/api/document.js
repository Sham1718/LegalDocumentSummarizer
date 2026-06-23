import api from "../utils/axios";

export const uploadDocument = (formData) => {
  return api.post(
    "/api/document/upload",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );
};
