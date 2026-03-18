<script setup name="OAPageHeader">
import { useRouter } from "vue-router"
import {defineProps} from "vue"

const router = useRouter()

const goBack = () => {
    router.go(-1)
}

let props = defineProps({
    content: ""
})
</script>

<template>
    <el-page-header @back="goBack" title="Back" class="custom-page-header">
        <template #content>
            <div class="content-wrapper">
                <span class="title-accent"></span>
                <span class="text-large font-600 mr-3 title-text"> {{ props.content }} </span>
            </div>
        </template>
    </el-page-header>
</template>

<style scoped>
.custom-page-header {
    padding: 16px 20px;
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    transition: all 0.3s ease;
}

.content-wrapper {
    display: flex;
    align-items: center;
}

.title-accent {
    width: 4px;
    height: 18px;
    background: linear-gradient(to bottom, #38bdf8, #818cf8);
    border-radius: 2px;
    margin-right: 12px;
}

.title-text {
    font-size: 18px;
    color: #1e293b;
    letter-spacing: -0.025em;
}

:deep(.el-page-header__back) {
    color: #64748b;
    transition: color 0.2s;
}

:deep(.el-page-header__back:hover) {
    color: #38bdf8;
}

:deep(.el-page-header__title) {
    font-size: 14px;
    font-weight: 500;
}

@media (max-width: 768px) {
    .custom-page-header {
        padding: 12px 15px;
    }
    .title-text {
        font-size: 16px;
    }
}
</style>