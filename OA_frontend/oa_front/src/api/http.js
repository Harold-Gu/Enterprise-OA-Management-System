import axios from "axios"
import { useAuthStore } from "@/stores/auth";

class Http{
    constructor(){
        this.instance = axios.create({
            baseURL: import.meta.env.VITE_BASE_URL,
            timeout: 6000
        });

        this.instance.interceptors.request.use((config) => {
            const authStore = useAuthStore()
            const token = authStore.token
            if(token){
                config.headers.Authorization = "JWT " + token
            }
            return config
        })
    }

    post(path, data){
        // path: /auth/login
        // url: http://127.0.0.1:8000/auth/login
        // return this.instance.post(path, data)
        return new Promise(async (resolve, reject) => {
            // await: After sending the network request, the thread suspends and waits
            // After network data arrives, the thread returns to the current position and continues execution
            // If await is used in a function, that function must be defined as async
            // axios internally also uses Promise objects. When the response status code is not 200, reject will be called
            // The result of calling reject is that the outer function throws an exception
            try{
                let result = await this.instance.post(path, data)
                // If the code below is reached, it means the await function above did not throw an exception, so the returned status code is definitely 200
                resolve(result.data);
            }catch(err){
                // When we reach catch, it means the status code is definitely not 200
                try{
                    let detail = err.response.data.detail;
                    reject(detail)
                }catch{
                    reject('Server error!')
                }
            }
        })
    }

    get(path, params){
        return new Promise(async (resolve, reject) => {
            try{
                let result = await this.instance.get(path, {params})
                resolve(result.data)
            }catch(err){
                let detail = err.response.data.detail;
                reject(detail)
            }
        })
    }

    put(path, data){
        return new Promise(async (resolve, reject) => {
            try{
                let result = await this.instance.put(path, data)
                resolve(result.data);
            }catch(err){
                let detail = err.response.data.detail;
                reject(detail)
            }
        })
    }

    delete(path){
        return new Promise(async (resolve, reject) => {
            try{
                let result = await this.instance.delete(path)
                // Because the delete method on the server side only returns a status code without data, we can directly return result
                resolve(result);
            }catch(err){
                let detail = err.response.data.detail;
                reject(detail)
            }
        })
    }

    downloadFile(path, params){
        return new Promise(async (resolve, reject) => {
            try{
                let result = await this.instance.get(path, {
                    params,
                    responseType: "blob"
                })
                resolve(result)
            }catch(err){
                let detail = err.response.data.detail;
                reject(detail)
            }
        })
    }
}

export default new Http()