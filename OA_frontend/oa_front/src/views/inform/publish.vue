<script setup name="publishinform">
import OAMain from '@/components/OAMain.vue';
import { ref, reactive, onBeforeUnmount, shallowRef, onMounted } from "vue"
import '@wangeditor/editor/dist/css/style.css' 
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { i18nChangeLanguage } from '@wangeditor/editor' 
import staffHttp from '@/api/staffHttp';
import { ElMessage } from "element-plus"
import { useAuthStore } from '@/stores/auth';
import informHttp from '@/api/informHttp';
import { useRouter } from 'vue-router'; 

i18nChangeLanguage('en')

const authStore = useAuthStore()
const router = useRouter() 

let isLoading = ref(false) 

let informForm = reactive({
    title: '',
    content: '',
    department_ids: []
})
const rules = reactive({
    title: [{ required: true, message: "Please enter a title!", trigger: 'blur' }],
    content: [{ required: true, message: "Please enter content!", trigger: 'blur' }],
    department_ids: [{ required: true, message: "Please select departments!", trigger: 'change' }]
})
let formRef = ref()
let formLabelWidth = "120px"
let departments = ref([])

////////////// This is wangEditor related configuration //////////////
// Editor instance, must use shallowRef
const editorRef = shallowRef()

const toolbarConfig = {}
const editorConfig = {
    placeholder: 'Please enter content...',
    MENU_CONF: {

        fontFamily: {
            fontFamilyList: [
                'Arial', 
                'Tahoma', 
                'Verdana', 
                'Times New Roman', 
                'Courier New'
            ]
        },
        uploadImage: {
            server: import.meta.env.VITE_BASE_URL + '/image/upload',
            fieldName: 'image',
            maxFileSize: 0.5 * 1024 * 1024,
            maxNumberOfFiles: 10,
            allowedFileTypes: ['image/*'],
            headers: {
                Authorization: "JWT " + authStore.token
            },
            timeout: 6 * 1000, // 6 seconds,
            customInsert(res, insertFn) {
                if(res.errno == 0){
                    let data = res.data;
                    let url = import.meta.env.VITE_BASE_URL + data.url
                    let href = import.meta.env.VITE_BASE_URL + data.href
                    let alt = data.alt;
                    insertFn(url, alt, href)
                }else{
                    ElMessage.error(res.message)
                }
            },
            onFailed(file, res) {
                console.log(`${file.name} upload failed`, res)
            },
            onError(file, err, res) {
                if(file.size > 0.5*1024*1024){
                    ElMessage.error('Image file size cannot exceed 0.5MB!')
                }else{
                    ElMessage.error('Image format is incorrect!')
                }
            },
        }
    }
}
let mode = "default"

// When component is destroyed, also destroy editor in time
onBeforeUnmount(() => {
    const editor = editorRef.value
    if (editor == null) return
    editor.destroy()
})

const handleCreated = (editor) => {
    editorRef.value = editor // Record editor instance, important!
}
////////////// This is wangEditor related configuration //////////////

onMounted(async () => {
    try {
        let data = await staffHttp.getAllDepartment()
        departments.value = data.results
    } catch (detail) {
        ElMessage.error(detail)
    }
})

const onSubmit = () => {
    formRef.value.validate(async (valid, fields) => {
        if (valid) {
            isLoading.value = true; // 
            try{
                await informHttp.publishInform(informForm)
                

                ElMessage.success("Notification published successfully!")
                

                router.push({ name: 'inform_list' })
                
            }catch(detail){
                ElMessage.error(detail)
            }finally{
                isLoading.value = false; 
            }
        }
    })
}

</script>

<template>
    <OAMain title="Publish Notification">
        <el-card class="publish-card">
            <template #header>
                <div class="card-header-tech">
                    <span class="header-dot"></span>
                    <span class="header-title">Compose Notification</span>
                </div>
            </template>
            
            <el-form :model="informForm" :rules="rules" ref="formRef" label-position="top">
                <el-row :gutter="40">
                    <el-col :span="14" :xs="24">
                        <el-form-item label="Notification Title" prop="title" class="tech-form-item">
                            <el-input 
                                v-model="informForm.title" 
                                autocomplete="off" 
                                placeholder="Enter a descriptive title..."
                                class="tech-input"
                            />
                        </el-form-item>
                    </el-col>
                    <el-col :span="10" :xs="24">
                        <el-form-item label="Target Departments" prop="department_ids" class="tech-form-item">
                            <el-select 
                                multiple 
                                v-model="informForm.department_ids" 
                                placeholder="Select visibility..." 
                                style="width: 100%"
                                class="tech-select"
                                collapse-tags
                                collapse-tags-tooltip
                            >
                                <el-option :value="0" label="All Departments"></el-option>
                                <el-option v-for="department in departments" :label="department.name" :value="department.id"
                                    :key="department.name" />
                            </el-select>
                        </el-form-item>
                    </el-col>
                </el-row>

                <el-form-item label="Detailed Content" prop="content" class="tech-form-item">
                    <div class="editor-wrapper">
                        <Toolbar 
                            class="tech-toolbar"
                            :editor="editorRef"
                            :defaultConfig="toolbarConfig" 
                            :mode="mode" 
                        />
                        <Editor 
                            class="tech-editor"
                            style="height: 520px; overflow-y: hidden;" 
                            v-model="informForm.content"
                            :defaultConfig="editorConfig" 
                            :mode="mode" 
                            @onCreated="handleCreated" 
                        />
                    </div>
                </el-form-item>

                <div class="form-footer">
                    <el-button 
                        type="primary" 
                        :loading="isLoading" 
                        @click="onSubmit"
                        class="publish-btn"
                        icon="Promotion"
                    >
                        Publish Notification
                    </el-button>
                </div>
            </el-form>
        </el-card>
    </OAMain>
</template>

<style scoped>
.publish-card {
    border: none;
    border-radius: 16px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
}

.card-header-tech {
    display: flex;
    align-items: center;
}

.header-dot {
    width: 8px;
    height: 8px;
    background: #38bdf8;
    border-radius: 50%;
    margin-right: 12px;
}

.header-title {
    font-weight: 600;
    color: #1e293b;
    font-size: 16px;
}

.tech-form-item :deep(.el-form-item__label) {
    font-weight: 600;
    color: #64748b;
    padding-bottom: 8px;
}

.editor-wrapper {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
    width: 100%;
    transition: border-color 0.3s;
}

.editor-wrapper:focus-within {
    border-color: #38bdf8;
}

.tech-toolbar {
    border-bottom: 1px solid #f1f5f9 !important;
    background: #f8fafc !important;
}

.tech-editor {
    background: #fff;
}

.form-footer {
    display: flex;
    justify-content: flex-end;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #f1f5f9;
}

.publish-btn {
    padding: 12px 30px;
    height: auto;
    font-size: 15px;
    font-weight: 600;
    border-radius: 12px;
    background: linear-gradient(135deg, #38bdf8 0%, #6366f1 100%) !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
}

.publish-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(56, 189, 248, 0.4);
}

:deep(.el-input__wrapper), :deep(.el-select__wrapper) {
    box-shadow: 0 0 0 1px #e2e8f0 inset;
    border-radius: 10px;
    padding: 8px 12px;
}

:deep(.el-input__wrapper.is-focus), :deep(.el-select__wrapper.is-focus) {
    box-shadow: 0 0 0 1px #38bdf8 inset !important;
}

@media (max-width: 768px) {
    .publish-btn {
        width: 100%;
    }
}
</style>