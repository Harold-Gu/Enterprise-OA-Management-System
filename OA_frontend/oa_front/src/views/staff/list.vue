<script setup name="stafflist">
import OAMain from '@/components/OAMain.vue';
import { ref, reactive, onMounted, watch } from "vue";
import timeFormatter from '@/utils/timeFormatter';
import staffHttp from '@/api/staffHttp';
import { ElMessage } from 'element-plus';
import OADialog from '@/components/OADialog.vue';
import { useAuthStore } from '@/stores/auth';


const authStore = useAuthStore()

let staffs = ref([])
let pagination = reactive({
    page: 1,
    total: 0
})
let page_size = ref(10)
let dialogVisible = ref(false)
let staffForm = reactive({
    status: 1
})
let handleIndex = 0
let departments = ref([])
let filterForm = reactive({
    department_id: null,
    realname: "",
    date_joined: []
})
let tableRef = ref()
const BASE_URL = import.meta.env.VITE_BASE_URL


async function fetchStaffList(page, page_size) {
    try {
        // Get staff list
        let data = await staffHttp.getStaffList(page, page_size, filterForm)
        pagination.total = data.count
        pagination.page = page
        staffs.value = data.results
    } catch (detail) {
        ElMessage.error(detail)
    }
}

onMounted(async () => {
    fetchStaffList(1, page_size.value)

    try {
        let data = await staffHttp.getAllDepartment()
        departments.value = data.results;
    } catch (detail) {
        ElMessage.error(detail)
    }
})

watch(() => pagination.page, async function (value) {
    fetchStaffList(value, page_size.value)
})

watch(page_size, function (value) {
    if (pagination.page == 1) {
        fetchStaffList(1, value)
    } else {
        pagination.page = 1
    }
})

const onEditStaff = (index) => {
    handleIndex = index
    dialogVisible.value = true;
    let staff = staffs.value[index]
    staffForm.status = staff.status
}

const onSubmitEditStaff = async () => {
    let staff = staffs.value[handleIndex]
    try {
        let newstaff = await staffHttp.updateStaffStatus(staff.uid, staffForm.status)
        ElMessage.success("Staff status updated successfully!")
        dialogVisible.value = false;
        staffs.value.splice(handleIndex, 1, newstaff)
    } catch (detail) {
        ElMessage.error(detail)
    }
}

const onSearch = () => {
    fetchStaffList(1, page_size.value)
}

const onDownload = async () => {
    let rows = tableRef.value.getSelectionRows()
    if(!rows || rows.length==0){
        ElMessage.info('Please select staff to export first!')
        return;
    }
    try{
        let response = await staffHttp.downloadStaffs(rows.map(row => row.uid))
        // Use a tag to create URL object from response data
        // Create URL object from returned binary data
        let href = URL.createObjectURL(response.data)
        // Create a tag
        const a = document.createElement("a")
        a.href = href
        // Set download attribute on a tag, clicking will trigger download
        a.setAttribute('download', 'Staff Info.xlsx')
        // Add a tag to web structure
        document.body.appendChild(a)
        // Simulate click behavior to trigger download
        a.click()

        // After download, remove a tag as it's no longer needed
        document.body.removeChild(a)
        // Revoke URL data
        URL.revokeObjectURL(href)
    }catch(detail){
        ElMessage.error(detail)
    }
}

const onUploadSuccess = () => {
    ElMessage.success("Staff uploaded successfully!")
    // Re-fetch first page of staff data
    fetchStaffList(1, page_size.value)
}

const onUploadFail = (error) => {
    const detail = JSON.parse(error.message).detail
    ElMessage.error(detail)
}

</script>

<template>
    <OADialog title="Update Staff Status" v-model="dialogVisible" @submit="onSubmitEditStaff">
        <el-form :model="staffForm" label-width="100px">
            <el-form-item label="Status">
                <el-radio-group v-model="staffForm.status" class="ml-4">
                    <el-radio :value="1">Activated</el-radio>
                    <el-radio :value="3">Locked</el-radio>
                </el-radio-group>
            </el-form-item>
        </el-form>
    </OADialog>
    <OAMain title="Staff List">
        <el-card class="filter-card">
            <el-form :inline="true" class="my-form-inline">
                <el-form-item label="Department">
                    <el-select v-model="filterForm.department_id" placeholder="All" clearable>
                        <el-option v-for="department in departments" :label="department.name" :value="department.id"
                            :key="department.name" />
                    </el-select>
                </el-form-item>
                <el-form-item label="Name">
                    <el-input v-model="filterForm.realname" placeholder="Search name..." />
                </el-form-item>
                <el-form-item label="Joined Date">
                    <el-date-picker v-model="filterForm.date_joined" type="daterange" range-separator="-"
                        start-placeholder="Start" end-placeholder="End" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" icon="Search" @click="onSearch" class="tech-btn">Search</el-button>
                </el-form-item>
                <div class="action-buttons">
                    <el-form-item>
                        <el-button type="info" icon="Download" @click="onDownload" plain>Download</el-button>
                    </el-form-item>
                    <el-form-item>
                        <el-upload
                            :action="BASE_URL+'/staff/upload'"
                            :headers="{Authorization: 'JWT '+authStore.token}"
                            :on-success="onUploadSuccess"
                            :on-error="onUploadFail"
                            :show-file-list="false"
                            :auto-upload="true"
                            accept=".xlsx, .xls">
                            <el-button type="warning" icon="Upload" plain>Upload</el-button>
                        </el-upload>
                    </el-form-item>
                </div>
            </el-form>
        </el-card>

        <el-card class="table-card">
            <el-table :data="staffs" ref="tableRef" stripe highlight-current-row scrollbar-always-on>
                <el-table-column type="selection" width="55"></el-table-column>
                <el-table-column label="No." width="70">
                    <template #default="scope">
                        <span class="index-number">{{ scope.$index + 1 }}</span>
                    </template>
                </el-table-column>
                <el-table-column prop="realname" label="Name" font-weight="600"></el-table-column>
                <el-table-column prop="email" label="Email" min-width="180"></el-table-column>
                <el-table-column label="Joining Date" width="150">
                    <template #default="scope">
                        <span class="date-text">{{ timeFormatter.stringFromDate(scope.row.date_joined) }}</span>
                    </template>
                </el-table-column>
                <el-table-column prop="department.name" label="Department"></el-table-column>
                <el-table-column label="Status" width="120">
                    <template #default="scope">
                        <el-tag v-if="scope.row.status == 1" type="success" effect="light" round>Normal</el-tag>
                        <el-tag v-else-if="scope.row.status == 2" type="warning" effect="light" round>Inactive</el-tag>
                        <el-tag v-else type="danger" effect="light" round>Locked</el-tag>
                    </template>
                </el-table-column>
                <el-table-column label="Actions" width="100" fixed="right">
                    <template #default="scope">
                        <el-button type="primary" icon="Edit" circle @click="onEditStaff(scope.$index)" class="edit-btn"></el-button>
                    </template>
                </el-table-column>
            </el-table>

            <template #footer>
                <div class="pagination-container">
                    <el-form-item label="Display" class="per-page-selector">
                        <el-select v-model="page_size" size="small" style="width: 120px;">
                            <el-option label="10 / page" :value="10" />
                            <el-option label="20 / page" :value="20" />
                            <el-option label="50 / page" :value="50" />
                        </el-select>
                    </el-form-item>
                    <el-pagination 
                        background 
                        layout="prev, pager, next" 
                        :total="pagination.total"
                        v-model:currentPage="pagination.page" 
                        :page-size="page_size" 
                    />
                </div>
            </template>
        </el-card>
    </OAMain>
</template>

<style scoped>
.filter-card {
    margin-bottom: 20px;
    border: none;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
}

.table-card {
    border: none;
    border-radius: 16px;
    overflow: hidden;
}

.action-buttons {
    display: inline-flex;
    margin-left: 10px;
}

.tech-btn {
    padding-left: 25px;
    padding-right: 25px;
    font-weight: 500;
}

.edit-btn {
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
}

.index-number {
    color: #94a3b8;
    font-weight: 500;
}

.date-text {
    color: #64748b;
}

.pagination-container {
    display: flex; 
    justify-content: space-between; 
    align-items: center;
    padding: 10px 0;
}

.per-page-selector {
    margin-bottom: 0;
}

:deep(.el-table__header) {
    background-color: #f8fafc;
}

:deep(.el-table__row) {
    height: 60px;
}

/* Responsive micro-adjustments */
@media (max-width: 768px) {
    .action-buttons {
        display: flex;
        margin-top: 10px;
        margin-left: 0;
    }
    .my-form-inline .el-form-item {
        margin-right: 10px;
    }
}
</style>