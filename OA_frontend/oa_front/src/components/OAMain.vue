<script setup>
import OAPageHeader from "@/components/OAPageHeader.vue"
import {defineProps} from "vue"

let props = defineProps({
    title: ""
})

</script>

<template>
<el-space direction="vertical" fill :size="20" style="width: 100%">
    <OAPageHeader :content="props.title"></OAPageHeader>
    <slot></slot>
</el-space>
</template>

<style scoped>
.el-space :deep(.el-space__item){
    width: 100%;
}

@media (max-width: 768px) {
    :deep(.el-page-header__content) {
        font-size: 16px;
    }
}
</style>