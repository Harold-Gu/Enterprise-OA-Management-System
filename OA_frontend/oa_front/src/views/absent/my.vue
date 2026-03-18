<script setup name="myabsent">
import OAPageHeader from "@/components/OAPageHeader.vue"
import absentHttp from "@/api/absentHttp";
import { ref, reactive, onMounted, computed, watch } from "vue"
import { ElMessage } from "element-plus"
import timeFormatter from "@/utils/timeFormatter";
import OAMain from "@/components/OAMain.vue"
import OAPagination from "@/components/OAPagination.vue"
import OADialog from "@/components/OADialog.vue"


let formLabelWidth = "120px"
let dialogFormVisible = ref(false)
let absentForm = reactive({
    title: '',
    absent_type_id: null,
    date_range: [],
    request_content: ""
})
let absentFormRef = ref()
let rules = reactive({
    title: [
        { required: true, message: 'Please enter a title!', trigger: 'blur' }
    ],
    absent_type_id: [
        { required: true, message: 'Please select leave type!', trigger: 'change' }
    ],
    date_range: [
        { required: true, message: 'Please select leave time!', trigger: 'blur' }
    ],
    request_content: [
        { required: true, message: 'Please enter the reason for leave!', trigger: 'blur' }
    ]
})
// Personal attendance information
let absents = ref([])
let absent_types = ref([])
let responder = reactive({
    email: '',
    realname: ''
})
let pagination = reactive({
    total: 0,
    page: 1
})
let responder_str = computed(() => {
    if (responder.email) {
        return '[' + responder.email + ']' + responder.realname
    } else {
        return "No"
    }
})

watch(() => pagination.page, (value) => {
    requestAbsents(value);
})

const requestAbsents = async (page) => {
    try {
        let absents_data = await absentHttp.getMyAbsents(page)
        let total = absents_data.count;
        pagination.total = total
        let results = absents_data.results;
        absents.value = results;
    } catch (detail) {
        ElMessage.error(detail);
    }
}

const onShowDialog = () => {
    absentForm.title = ""
    absentForm.absent_type_id = null
    absentForm.date_range = []
    absentForm.request_content = ""
    dialogFormVisible.value = true;
}

const onSubmitAbsent = () => {
    absentFormRef.value.validate(async (valid, fields) => {
        if (valid) {
            let data = {
                title: absentForm.title,
                absent_type_id: absentForm.absent_type_id,
                start_date: absentForm.date_range[0],
                end_date: absentForm.date_range[1],
                request_content: absentForm.request_content
            }
            // console.log(data);
            try {
                let absent = await absentHttp.applyAbsent(data)
                dialogFormVisible.value = false;
                // console.log(absent);
                absents.value.unshift(absent)
                // Show a prompt after successfully initiating leave
                ElMessage.success('Leave application submitted successfully!');
            } catch (detail) {
                ElMessage.error(detail)
            }
        }
    })
}

onMounted(async () => {
    try {
        // 1. Get leave types
        let absent_types_data = await absentHttp.getAbsentTypes()
        absent_types.value = absent_types_data

        // 2. Get approver
        let responder_data = await absentHttp.getResponder()
        Object.assign(responder, responder_data)

        // 3. Get personal attendance list
        requestAbsents(1)
    } catch (detail) {
        ElMessage.error(detail)
    }
})


</script>

<template>
    <OAMain title="Personal Attendance">
        <div class="action-bar">
            <el-button type="primary" size="large" @click="onShowDialog" class="tech-apply-btn">
                <el-icon style="margin-right: 8px;"><Plus /></el-icon>
                Apply for Leave
            </el-button>
        </div>

        <el-card class="attendance-card">
            <template #header>
                <div class="card-header-tech">
                    <span class="header-dot"></span>
                    <span class="header-text">My Application Records</span>
                </div>
            </template>

            <el-table :data="absents" stripe highlight-current-row class="tech-table">
                <el-table-column prop="title" label="Title" min-width="150">
                    <template #default="scope">
                        <span class="title-text">{{ scope.row.title }}</span>
                    </template>
                </el-table-column>
                
                <el-table-column prop="absent_type.name" label="Type" width="120">
                    <template #default="scope">
                        <el-tag effect="plain" class="type-tag">{{ scope.row.absent_type.name }}</el-tag>
                    </template>
                </el-table-column>

                <el-table-column label="Duration" min-width="200">
                    <template #default="scope">
                        <div class="date-range-text">
                            <el-icon class="date-icon"><Calendar /></el-icon>
                            {{ scope.row.start_date }} <span class="arrow">➔</span> {{ scope.row.end_date }}
                        </div>
                    </template>
                </el-table-column>

                <el-table-column label="Review Status" width="150" align="center">
                    <template #default="scope">
                        <el-tag type="info" effect="light" round v-if="scope.row.status == 1">Pending Review</el-tag>
                        <el-tag type="success" effect="light" round v-else-if="scope.row.status == 2">Approved</el-tag>
                        <el-tag type="danger" effect="light" round v-else>Rejected</el-tag>
                    </template>
                </el-table-column>

                <el-table-column label="Approver" min-width="150">
                    <template #default="scope">
                        <span class="responder-text">{{ responder_str }}</span>
                    </template>
                </el-table-column>

                <el-table-column prop="response_content" label="Feedback" min-width="150" show-overflow-tooltip />
            </el-table>

            <template #footer>
                <div class="pagination-wrapper">
                    <OAPagination v-model="pagination.page" :total="pagination.total"></OAPagination>
                </div>
            </template>
        </el-card>
    </OAMain>

    <OADialog title="Apply for Leave" v-model="dialogFormVisible" @submit="onSubmitAbsent" :width="isMobile ? '92%' : '560px'">
        <template #header>
            <div class="dialog-header-custom">
                <el-icon class="header-icon"><EditPen /></el-icon>
                <span>Leave Application</span>
            </div>
        </template>
        
        <el-form :model="absentForm" :rules="rules" ref="absentFormRef" label-position="top" class="tech-form">
            <el-form-item label="Application Title" prop="title">
                <el-input v-model="absentForm.title" placeholder="e.g., Annual Leave for Trip" />
            </el-form-item>
            
            <el-row :gutter="20">
                <el-col :span="12" :xs="24">
                    <el-form-item label="Leave Type" prop="absent_type_id">
                        <el-select v-model="absentForm.absent_type_id" placeholder="Select type" style="width: 100%">
                            <el-option v-for="item in absent_types" :label="item.name" :value="item.id" :key="item.name" />
                        </el-select>
                    </el-form-item>
                </el-col>
                <el-col :span="12" :xs="24">
                    <el-form-item label="Approving Leader">
                        <el-input :value="responder_str" readonly disabled />
                    </el-form-item>
                </el-col>
            </el-row>

            <el-form-item label="Date Range" prop="date_range">
                <el-date-picker 
                    v-model="absentForm.date_range" 
                    type="daterange" 
                    range-separator="to"
                    start-placeholder="Start Date" 
                    end-placeholder="End Date" 
                    format="YYYY-MM-DD" 
                    value-format="YYYY-MM-DD"
                    style="width: 100%" 
                />
            </el-form-item>

            <el-form-item label="Reason for Leave" prop="request_content">
                <el-input type="textarea" :rows="4" v-model="absentForm.request_content" placeholder="Please describe the reason for your application..." />
            </el-form-item>
        </el-form>
    </OADialog>
</template>

<style scoped>
.action-bar {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 24px;
}

.tech-apply-btn {
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    background: linear-gradient(135deg, #38bdf8 0%, #6366f1 100%) !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
    transition: all 0.3s;
}

.tech-apply-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(56, 189, 248, 0.4);
}

.attendance-card {
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

.header-text {
    font-weight: 600;
    color: #1e293b;
    font-size: 16px;
}

.title-text {
    font-weight: 600;
    color: #334155;
}

.type-tag {
    border-radius: 6px;
    font-weight: 500;
}

.date-range-text {
    display: flex;
    align-items: center;
    font-size: 13px;
    color: #64748b;
}

.date-icon {
    margin-right: 6px;
    color: #94a3b8;
}

.arrow {
    margin: 0 8px;
    color: #cbd5e1;
}

.responder-text {
    font-size: 13px;
    color: #475569;
}

.pagination-wrapper {
    display: flex;
    justify-content: flex-end;
    padding: 10px 0;
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

.tech-form :deep(.el-form-item__label) {
    font-weight: 600;
    color: #64748b;
}

:deep(.el-table__row) {
    height: 65px;
}

:deep(.el-table__header th) {
    background-color: #f8fafc;
    color: #475569;
    font-weight: 600;
}

@media (max-width: 768px) {
    .action-bar {
        justify-content: center;
    }
    .tech-apply-btn {
        width: 100%;
    }
}
</style>