<script setup name="subabsent">
import OAPageHeader from "@/components/OAPageHeader.vue"
import absentHttp from "@/api/absentHttp";
import { ref, reactive, onMounted } from "vue"
import { ElMessage } from "element-plus"
import timeFormatter from "@/utils/timeFormatter";
import OAMain from "@/components/OAMain.vue"
import OAPagination from "@/components/OAPagination.vue"
import OADialog from "@/components/OADialog.vue";


let absents = ref([])
let pagination = reactive({
    total: 0,
    page: 1
})
let dialogVisible = ref(false)
let absentForm = reactive({
    status: 2,
    response_content: ""
})
let rules = reactive({
    status: [{ required: true, message: 'Please select result!', trigger: 'change' }],
    response_content: [{ required: true, message: 'Please enter reason!', trigger: "blur" }]
})
let absentFormRef = ref()
let handleIndex = null

onMounted(async () => {
    try {
        let data = await absentHttp.getSubAbsents()
        pagination.total = data.count;
        absents.value = data.results;
    } catch (detail) {
        ElMessage.error(detail)
    }
})

const onShowDialog = (index) => {
    absentForm.status = 2;
    absentForm.response_content = ""
    dialogVisible.value = true;
    handleIndex = index
}
const onSubmitAbsent = () => {
    absentFormRef.value.validate(async (valid, fields) => {
        if(valid){
            try{
                // Hide dialog
                dialogVisible.value = false;
                const absent = absents.value[handleIndex]
                const data = await absentHttp.handleSubAbsent(absent.id, absentForm.status, absentForm.response_content)
                // console.log(data);
                absents.value.splice(handleIndex, 1, data)
                ElMessage.success('Subordinate attendance handled successfully!');
            }catch(detail){
                ElMessage.error(detail)
            }
        }
    })
}
</script>

<template>
    <OADialog title="Handle Attendance" v-model="dialogVisible" @submit="onSubmitAbsent" width="500px">
        <template #header>
            <div class="dialog-header-tech">
                <el-icon class="header-icon"><Checked /></el-icon>
                <span>Approval Decision Center</span>
            </div>
        </template>
        <el-form :model="absentForm" :rules="rules" ref="absentFormRef" label-position="top" class="tech-form">
            <el-form-item label="Approval Result" prop="status">
                <el-radio-group v-model="absentForm.status" class="tech-radio-group">
                    <el-radio :value="2" border class="approve-radio">Approved</el-radio>
                    <el-radio :value="3" border class="reject-radio">Rejected</el-radio>
                </el-radio-group>
            </el-form-item>
            <el-form-item label="Review Comments" prop="response_content">
                <el-input 
                    type="textarea" 
                    :rows="4"
                    v-model="absentForm.response_content" 
                    placeholder="Enter the reason for approval or rejection..."
                    autocomplete="off" 
                />
            </el-form-item>
        </el-form>
    </OADialog>

    <OAMain title="Subordinate Attendance">
        <el-card class="table-card">
            <template #header>
                <div class="card-header-tech">
                    <span class="header-dot"></span>
                    <span class="header-text">Pending & History Requests</span>
                </div>
            </template>

            <el-table :data="absents" stripe highlight-current-row class="tech-table">
                <el-table-column label="Requester" width="180">
                    <template #default="scope">
                        <div class="requester-info">
                            <span class="dept-name">{{ scope.row.requester.department.name }}</span>
                            <span class="real-name">{{ scope.row.requester.realname }}</span>
                        </div>
                    </template>
                </el-table-column> 

                <el-table-column prop="title" label="Subject" min-width="150" />
                
                <el-table-column label="Leave Details" min-width="220">
                    <template #default="scope">
                        <div class="type-box">
                            <el-tag size="small" effect="plain" class="type-tag">{{ scope.row.absent_type.name }}</el-tag>
                            <div class="date-range">
                                {{ scope.row.start_date }} <span class="arrow">➔</span> {{ scope.row.end_date }}
                            </div>
                        </div>
                    </template>
                </el-table-column>

                <el-table-column label="Status" width="140" align="center">
                    <template #default="scope">
                        <el-tag type="info" effect="light" round v-if="scope.row.status == 1">Pending</el-tag>
                        <el-tag type="success" effect="light" round v-else-if="scope.row.status == 2">Approved</el-tag>
                        <el-tag type="danger" effect="light" round v-else>Rejected</el-tag>
                    </template>
                </el-table-column>

                <el-table-column label="Feedback" min-width="150" show-overflow-tooltip>
                    <template #default="scope">
                        <span class="feedback-text">{{ scope.row.response_content || '-' }}</span>
                    </template>
                </el-table-column>

                <el-table-column label="Operation" width="100" align="center" fixed="right">
                    <template #default="scope">
                        <el-button 
                            v-if="scope.row.status == 1" 
                            @click="onShowDialog(scope.$index)" 
                            type="primary" 
                            icon="EditPen" 
                            circle
                            class="handle-btn"
                        />
                        <el-tag v-else type="info" effect="plain" class="handled-label">Handled</el-tag>
                    </template>
                </el-table-column>
            </el-table>

            <template #footer>
                <div class="pagination-wrapper">
                    <OAPagination v-model="pagination.page" :total="pagination.total"></OAPagination>
                </div>
            </template>
        </el-card>
    </OAMain>
</template>

<style scoped>
.table-card {
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

.requester-info {
    display: flex;
    flex-direction: column;
    line-height: 1.4;
}

.dept-name {
    font-size: 11px;
    color: #94a3b8;
    text-transform: uppercase;
    font-weight: 500;
}

.real-name {
    font-size: 14px;
    font-weight: 600;
    color: #334155;
}

.type-box {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.type-tag {
    align-self: flex-start;
    border-radius: 6px;
}

.date-range {
    font-size: 12px;
    color: #64748b;
}

.arrow {
    color: #cbd5e1;
    margin: 0 4px;
}

.feedback-text {
    font-size: 13px;
    color: #94a3b8;
}

.handle-btn {
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
    transition: transform 0.2s;
}

.handle-btn:hover {
    transform: scale(1.1);
}

.handled-label {
    border: none;
    background: transparent;
    color: #cbd5e1;
    font-size: 12px;
}

.pagination-wrapper {
    display: flex;
    justify-content: center;
    padding: 10px 0;
}

/* Dialog Tech Style */
.dialog-header-tech {
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

.tech-radio-group {
    display: flex;
    gap: 15px;
    width: 100%;
}

.tech-radio-group :deep(.el-radio) {
    flex: 1;
    margin-right: 0;
    height: 45px;
    border-radius: 10px;
    display: flex;
    justify-content: center;
}

.approve-radio.is-checked {
    border-color: #10b981 !important;
    background: #ecfdf5 !important;
}

.reject-radio.is-checked {
    border-color: #f43f5e !important;
    background: #fff1f2 !important;
}

:deep(.el-table__row) {
    height: 70px;
}

:deep(.el-table__header th) {
    background-color: #f8fafc;
    color: #475569;
    font-weight: 600;
}
</style>