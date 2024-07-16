import axios from "axios";

const instance = axios.create({

});

instance.interceptors.request.use(
    (config) => {
        config.headers['Authorization'] = "Bearer " + localStorage.getItem("token")
        return config;
    }
)
instance.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalConfig = error.config;
        if (error.response.status === 401 && !originalConfig._retry) {
            originalConfig._retry = true;
            await axios
                .get("http://localhost:8000/refresh", {
                    withCredentials: true,
                })
                .then(response => {
                    // instance.defaults.headers.common["Authorization"] = "Bearer " + res.data.access_token;
                    localStorage.setItem("token", response.data.access_token);
                })
                .catch((err) => {
                    return Promise.reject(err);
                });
            console.log(originalConfig);
            return instance(originalConfig);
        } else {
            return Promise.reject(error);
        }
    }
);
// instance.post('http://localhost:8000/llm/purpose',{'data': "1"})
// .then(response => {
//   console.log(response.data)
// })
// .catch(error => console.error(error));


export default instance;