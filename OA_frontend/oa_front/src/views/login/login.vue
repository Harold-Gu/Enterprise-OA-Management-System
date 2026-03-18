<script setup name="login">
import {reactive} from "vue"
import {useAuthStore} from "@/stores/auth"
import {useRouter} from "vue-router"
import authHttp from "@/api/authHttp"
import {ElMessage} from "element-plus"

const authStore = useAuthStore()
const router = useRouter()

let form = reactive({
    email: '',
    password: ''
})

const onSubmit = async () => {
    let pwdRgx = /^[a-zA-Z0-9]{6,20}$/
    let emailRgx = /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9])+/
    if(!(emailRgx.test(form.email))){
        ElMessage.info('The email format does not meet the requirements.')
        return;
    }
    if(!(pwdRgx.test(form.password))){
        ElMessage.info("The password format does not meet the requirements.")
        return;
    }
    
    try{
        let data = await authHttp.login(form.email, form.password)
        let token = data.token;
        let user = data.user;
        authStore.setUserToken(user, token);
        router.push({name: "home"})
    }catch(detail){
        ElMessage.error(detail)
    }
}

</script>

<template>
    <div class="dowebok">
        <div class="tech-bg-overlay"></div>
        
        <div class="container-login100">
            <div class="wrap-login100">
                <div class="login100-form validate-form">
                    <span class="login100-form-title tech-title"> 
                        <span class="title-main">EMPLOYEE LOGIN</span>
                        <span class="title-sub">Secure Access Portal</span>
                    </span>

                    <div class="wrap-input100 validate-input">
                        <input class="input100 tech-input" type="text" name="email" placeholder="Email Address" v-model="form.email" />
                        <span class="focus-input100"></span>
                        <span class="symbol-input100">
                            <i class="iconfont icon-fa-envelope" aria-hidden="true"></i>
                        </span>
                    </div>

                    <div class="wrap-input100 validate-input">
                        <input class="input100 tech-input" type="password" name="password" placeholder="Password" v-model="form.password" />
                        <span class="focus-input100"></span>
                        <span class="symbol-input100">
                            <i class="iconfont icon-fa-lock" aria-hidden="true"></i>
                        </span>
                    </div>

                    <div class="container-login100-form-btn">
                        <button class="login100-form-btn tech-btn" @click="onSubmit">
                            SIGN IN
                        </button>
                    </div>

                    <div class="system-notice tech-notice">
                        <div class="notice-header">
                            <i class="iconfont icon-fa-shield"></i> Security Notice
                        </div>
                        <p>Since it is an internal system of the company, there is no option for homepage registration. However, you can obtain the account and password by referring to the contents in the report to log in.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped src="@/assets/css/login.css"></style>
<style scoped src="@/assets/iconfont/iconfont.css"></style>

<style scoped>
.dowebok {
    position: relative;
    overflow: hidden;
    background: #0f172a;
}

.tech-bg-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 20% 30%, rgba(56, 189, 248, 0.15) 0%, transparent 40%),
        radial-gradient(circle at 80% 70%, rgba(99, 102, 241, 0.15) 0%, transparent 40%);
    animation: bgPulse 10s infinite alternate;
}

@keyframes bgPulse {
    0% { transform: scale(1); opacity: 0.8; }
    100% { transform: scale(1.1); opacity: 1; }
}

.container-login100 {
    background: transparent !important;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

.wrap-login100 {
    width: 550px !important;
    background: rgba(30, 41, 59, 0.7) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5) !important;
    border-radius: 24px !important;
    padding: 60px 55px !important;
    z-index: 10;
    display: flex;
    justify-content: center;
}

.login100-form {
    width: 100% !important;
}

.tech-title {
    color: #fff !important;
    font-family: 'Inter', sans-serif;
    display: flex;
    flex-direction: column;
    padding-bottom: 40px !important;
    text-align: center;
}

.title-main {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: 2px;
    background: linear-gradient(to right, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.title-sub {
    font-size: 12px;
    color: #94a3b8;
    margin-top: 5px;
    letter-spacing: 4px;
    text-transform: uppercase;
}

.tech-input {
    background: rgba(15, 23, 42, 0.5) !important;
    color: #fff !important;
    border-radius: 12px !important;
    height: 55px !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    transition: all 0.3s ease !important;
}

.tech-input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.2) !important;
}

.symbol-input100 {
    color: #38bdf8 !important;
}

.tech-btn {
    height: 55px !important;
    background: linear-gradient(135deg, #38bdf8 0%, #6366f1 100%) !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4) !important;
    transition: all 0.3s ease !important;
}

.tech-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(56, 189, 248, 0.6) !important;
    filter: brightness(1.1);
}

.tech-notice {
    background: rgba(15, 23, 42, 0.4);
    border: 1px dashed rgba(56, 189, 248, 0.3);
    border-radius: 12px;
    padding: 15px !important;
    margin-top: 40px !important;
}

.notice-header {
    color: #38bdf8;
    font-weight: 600;
    font-size: 12px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.tech-notice p {
    color: #94a3b8 !important;
    font-size: 12px !important;
    line-height: 1.5 !important;
    text-align: justify;
}

@media (max-width: 768px) {
    .wrap-login100 {
        width: 90% !important;
        padding: 40px 30px !important;
    }
}
</style>