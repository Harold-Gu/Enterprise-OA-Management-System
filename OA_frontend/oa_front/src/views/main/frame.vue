<script setup name="frame">
import { ref, computed, reactive, onMounted, onUnmounted } from "vue"
import {
    Expand,
    Fold,
    ArrowDown,
    UserFilled
} from '@element-plus/icons-vue'
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import authHttp from "@/api/authHttp";
import { ElMessage } from "element-plus";
import routes from "@/router/frame"

const authStore = useAuthStore()
const router = useRouter()

const isMobile = ref(false)
const drawerVisible = ref(false)
const checkIsMobile = () => {
    isMobile.value = window.innerWidth <= 768
}

let displayUser = reactive({
    department: {},
    realname: ""
})
let defaultActive = ref("home")
let isCollapse = ref(false);
let dialogVisible = ref(false)
let formLabelWidth = "120px"
let resetPwdForm = reactive({
    oldpwd: '',
    pwd1: '',
    pwd2: ''
})
let formTag = ref()

const validatePwd = (rule, value, callback) => {
    const pwdRegex = /^[a-zA-Z0-9]{6,20}$/
    if (!pwdRegex.test(value)) {
        callback(new Error('6-20 characters, letters and numbers only!'))
    } else {
        callback()
    }
}

let rules = reactive({
    oldpwd: [
        { required: true, message: 'Please enter your old password.', trigger: 'blur' },
        { validator: validatePwd, trigger: 'blur' },
    ],
    pwd1: [
        { required: true, message: 'Please enter a new password!', trigger: 'blur' },
        { validator: validatePwd, trigger: 'blur' },
    ],
    pwd2: [
        { required: true, message: 'Please enter the confirmation password!', trigger: 'blur' },
        { validator: validatePwd, trigger: 'blur' },
    ]
})

let asideWidth = computed(() => {
    if (isMobile.value) return "0px"
    if (isCollapse.value) {
        return "70px"
    } else {
        return "260px"
    }
})

onMounted(() => {
    checkIsMobile()
    window.addEventListener('resize', checkIsMobile)
    defaultActive.value = router.currentRoute.value.name
    displayUser.department = authStore.user.department
    displayUser.realname = authStore.user.realname
})

onUnmounted(() => {
    window.removeEventListener('resize', checkIsMobile)
})

const onToggleMenu = () => {
    if (isMobile.value) {
        drawerVisible.value = !drawerVisible.value
    } else {
        isCollapse.value = !isCollapse.value
    }
}

const onExit = () => {
    authStore.clearUserToken();
    router.push({ name: 'login' })
}

const onControlResetPwdDialog = () => {
    resetPwdForm.oldpwd = ""
    resetPwdForm.pwd1 = ""
    resetPwdForm.pwd2 = ""
    dialogVisible.value = true;
}

const onSubmit = () => {
    formTag.value.validate(async (valid, fields) => {
        if (valid) {
            try {
                await authHttp.resetPwd(resetPwdForm.oldpwd, resetPwdForm.pwd1, resetPwdForm.pwd2)
                ElMessage.success("Password modification successful!")
                dialogVisible.value = false;
            } catch (detail) {
                ElMessage.error(detail)
            }
        } else {
            ElMessage.info('Please fill in the fields as required!')
        }
    })
}

</script>

<template>
    <el-container class="container">
        <el-aside v-if="!isMobile" class="aside" :width="asideWidth">
            <div class="brand-wrapper">
                <router-link to="/" class="brand">
                    <div class="logo-box">OA</div>
                    <span v-show="!isCollapse" class="brand-text">System</span>
                </router-link>
            </div>
            
            <el-menu :router="true" active-text-color="#38bdf8" background-color="#0f172a" class="el-menu-vertical-demo"
                :default-active="defaultActive" text-color="#94a3b8" :collapse="isCollapse" :collapse-transition="false">
                <template v-for="route in routes[0].children">
                    <template v-if="authStore.has_permission(route.meta.permissions, route.meta.opt)">
                        <el-menu-item v-if="!route.children" :index="route.name" :route="{ name: route.name }">
                            <el-icon class="menu-icon">
                                <component :is="route.meta.icon"></component>
                            </el-icon>
                            <span>{{ route.meta.text }}</span>
                        </el-menu-item>

                        <el-sub-menu v-else :index="route.name">
                            <template #title>
                                <el-icon class="menu-icon">
                                    <component :is="route.meta.icon"></component>
                                </el-icon>
                                <span>{{ route.meta.text }}</span>
                            </template>
                            <template v-for="child in route.children">
                                <template v-if="authStore.has_permission(child.meta.permissions, child.meta.opt)">
                                    <el-menu-item v-if="!child.meta.hidden" :index="child.name"
                                        :route="{ name: child.name }">
                                        <el-icon class="menu-icon">
                                            <component :is="child.meta.icon"></component>
                                        </el-icon>
                                        <span>{{ child.meta.text }}</span>
                                    </el-menu-item>
                                </template>
                            </template>
                        </el-sub-menu>
                    </template>
                </template>
            </el-menu>
        </el-aside>

        <el-drawer v-model="drawerVisible" direction="ltr" size="280px" :with-header="false" class="mobile-drawer">
            <div class="brand-wrapper mobile-brand">
                <div class="logo-box">OA</div>
                <span class="brand-text">System</span>
            </div>
            <el-menu :router="true" active-text-color="#38bdf8" background-color="#0f172a" style="border:none"
                :default-active="defaultActive" text-color="#94a3b8" @select="drawerVisible = false">
                <template v-for="route in routes[0].children">
                    <template v-if="authStore.has_permission(route.meta.permissions, route.meta.opt)">
                        <el-menu-item v-if="!route.children" :index="route.name" :route="{ name: route.name }">
                            <el-icon><component :is="route.meta.icon"></component></el-icon>
                            <span>{{ route.meta.text }}</span>
                        </el-menu-item>
                        <el-sub-menu v-else :index="route.name">
                            <template #title>
                                <el-icon><component :is="route.meta.icon"></component></el-icon>
                                <span>{{ route.meta.text }}</span>
                            </template>
                            <template v-for="child in route.children">
                                <el-menu-item v-if="!child.meta.hidden && authStore.has_permission(child.meta.permissions, child.meta.opt)" :index="child.name" :route="{ name: child.name }">
                                    <el-icon><component :is="child.meta.icon"></component></el-icon>
                                    <span>{{ child.meta.text }}</span>
                                </el-menu-item>
                            </template>
                        </el-sub-menu>
                    </template>
                </template>
            </el-menu>
        </el-drawer>

        <el-container class="main-container">
            <el-header class="header">
                <div class="left-header">
                    <el-button class="toggle-btn" :icon="isCollapse || isMobile ? Expand : Fold" @click="onToggleMenu" text />
                </div>
                <el-dropdown trigger="click" class="user-dropdown">
                    <div class="el-dropdown-link">
                        <div class="user-profile">
                            <el-avatar :size="32" :icon="UserFilled" class="avatar-gradient" />
                            <div class="user-info-text">
                                <span class="dept-tag">{{ displayUser.department.name }}</span>
                                <span class="user-name">{{ displayUser.realname }}</span>
                            </div>
                            <el-icon class="el-icon--right"><arrow-down /></el-icon>
                        </div>
                    </div>
                    <template #dropdown>
                        <el-dropdown-menu class="tech-dropdown-menu">
                            <el-dropdown-item @click="onControlResetPwdDialog">
                                <el-icon><Lock /></el-icon>change password
                            </el-dropdown-item>
                            <el-dropdown-item divided @click="onExit" class="exit-item">
                                <el-icon><SwitchButton /></el-icon>log out
                            </el-dropdown-item>
                        </el-dropdown-menu>
                    </template>
                </el-dropdown>
            </el-header>
            
            <el-main class="main">
                <RouterView v-slot="{ Component }">
                    <transition name="fade-transform" mode="out-in">
                        <component :is="Component" />
                    </transition>
                </RouterView>
            </el-main>
        </el-container>
    </el-container>

    <el-dialog v-model="dialogVisible" title="Security Center" :width="isMobile ? '92%' : '460px'" custom-class="tech-dialog">
        <template #header>
            <div class="dialog-header-custom">
                <el-icon class="header-icon"><ShieldCheck /></el-icon>
                <span>Change Account Password</span>
            </div>
        </template>
        <el-form :model="resetPwdForm" :rules="rules" ref="formTag" :label-position="isMobile ? 'top' : 'right'">
            <el-form-item label="Old Password" :label-width="formLabelWidth" prop="oldpwd">
                <el-input v-model="resetPwdForm.oldpwd" autocomplete="off" type="password" show-password placeholder="Enter current password" />
            </el-form-item>

            <el-form-item label="New Password" :label-width="formLabelWidth" prop="pwd1">
                <el-input v-model="resetPwdForm.pwd1" autocomplete="off" type="password" show-password placeholder="6-20 chars (letters/numbers)" />
            </el-form-item>

            <el-form-item label="Confirm New" :label-width="formLabelWidth" prop="pwd2">
                <el-input v-model="resetPwdForm.pwd2" autocomplete="off" type="password" show-password placeholder="Repeat new password" />
            </el-form-item>
        </el-form>
        <template #footer>
            <div class="dialog-footer">
                <el-button @click="dialogVisible = false" round>Cancel</el-button>
                <el-button type="primary" @click="onSubmit" round class="submit-btn-tech">
                    Update Password
                </el-button>
            </div>
        </template>
    </el-dialog>
</template>

<style scoped>
.container {
    height: 100vh;
    background-color: #f8fafc;
}

.aside {
    background-color: #0f172a;
    transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    z-index: 1001;
}

.brand-wrapper {
    height: 70px;
    display: flex;
    align-items: center;
    padding: 0 20px;
    background-color: #0f172a;
}

.brand {
    display: flex;
    align-items: center;
    text-decoration: none;
    gap: 12px;
}

.logo-box {
    width: 34px;
    height: 34px;
    background: linear-gradient(135deg, #38bdf8 0%, #6366f1 100%);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 800;
    font-size: 14px;
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
}

.brand-text {
    color: white;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.el-menu {
    border-right: none;
    flex: 1;
}

:deep(.el-menu-item), 
:deep(.el-sub-menu__title) {
    height: 54px !important;
    line-height: 54px !important;
    margin: 4px 12px;
    border-radius: 10px;
    width: auto !important;
}

:deep(.el-menu-item.is-active) {
    background: rgba(56, 189, 248, 0.15) !important;
    color: #38bdf8 !important;
    font-weight: 600;
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
    background-color: rgba(255, 255, 255, 0.05) !important;
}

.header {
    height: 70px;
    background-color: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px;
    z-index: 1000;
}

.toggle-btn {
    font-size: 20px;
    color: #64748b;
}

.user-profile {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 6px 12px;
    border-radius: 12px;
    transition: background 0.2s;
}

.user-profile:hover {
    background: #f1f5f9;
}

.avatar-gradient {
    background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
    color: #0369a1;
}

.user-info-text {
    display: flex;
    flex-direction: column;
    margin-left: 12px;
    line-height: 1.2;
}

.dept-tag {
    font-size: 11px;
    color: #94a3b8;
    font-weight: 500;
    text-transform: uppercase;
}

.user-name {
    font-size: 14px;
    color: #1e293b;
    font-weight: 600;
}

.main {
    padding: 24px;
    background-color: #f8fafc;
}

/* Transitions */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-15px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(15px);
}

.dialog-header-custom {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 600;
}

.header-icon {
    color: #38bdf8;
    font-size: 20px;
}

.submit-btn-tech {
    background: linear-gradient(135deg, #38bdf8 0%, #6366f1 100%) !important;
    border: none;
}

@media (max-width: 480px) {
    .user-info-text, .el-icon--right {
        display: none;
    }
    .header {
        padding: 0 12px;
    }
}

:deep(.mobile-drawer .el-drawer__body) {
    padding: 0;
    background-color: #0f172a;
}

.mobile-brand {
    padding: 0 24px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
</style>