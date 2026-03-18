<script setup name="informlist">
import { ref, reactive, onMounted } from "vue"
import OAMain from "@/components/OAMain.vue";
import OADialog from "@/components/OADialog.vue";
import OAPagination from "@/components/OAPagination.vue";
import timeFormatter from "@/utils/timeFormatter"
import { useAuthStore } from "@/stores/auth";
import informHttp from "@/api/informHttp";
import { ElMessage } from "element-plus";

const authStore = useAuthStore()

let informs = ref([])
let pagination = reactive({
    page: 1,
    total: 0
})
let dialogVisible = ref(false)
let handleIndex = 0

onMounted(async () => {
    try {
        let data = await informHttp.getInformList(1)
        pagination.total = data.count
        informs.value = data.results
    } catch (detail) {
        ElMessage.error(detail)
    }
})


const onShowDialog = (index) => {
    handleIndex = index
    dialogVisible.value = true;
}

const onDeleteInform = async () => {
    try {
        let inform = informs.value[handleIndex]
        await informHttp.deleteInform(inform.id)
        informs.value.splice(handleIndex, 1)
        dialogVisible.value = false;
        ElMessage.success("Notification deleted successfully!")
    } catch (detail) {
        ElMessage.error(detail)
    }
}

</script>

<template>
    <OADialog v-model="dialogVisible" title="Confirm Delete" @submit="onDeleteInform">
        <div class="confirm-content">
            <el-icon class="warning-icon"><Warning /></el-icon>
            <span>Are you sure you want to delete this notification? This action cannot be undone.</span>
        </div>
    </OADialog>

    <OAMain title="Notification List">
        <el-card class="table-card">
            <template #header>
                <div class="card-header">
                    <span class="header-dot"></span>
                    <span class="header-text">Latest System Notifications</span>
                </div>
            </template>

            <el-table :data="informs" stripe highlight-current-row class="tech-table">
                <el-table-column label="Title" min-width="250">
                    <template #default="scope">
                        <div class="title-container">
                            <span v-if="scope.row.reads.length==0" class="unread-dot"></span>
                            <RouterLink 
                                :to="{ name: 'inform_detail', params: { pk: scope.row.id } }" 
                                class="inform-link"
                                :class="{ 'unread-title': scope.row.reads.length == 0 }"
                            >
                                {{ scope.row.title }}
                            </RouterLink>
                        </div>
                    </template>
                </el-table-column>

                <el-table-column label="Publisher" width="200">
                    <template #default="scope">
                        <div class="publisher-info">
                            <span class="dept-name">{{ scope.row.author.department.name }}</span>
                            <span class="author-name">{{ scope.row.author.realname }}</span>
                        </div>
                    </template>
                </el-table-column>

                <el-table-column label="Time" width="180">
                    <template #default="scope">
                        <span class="time-text">{{ timeFormatter.stringFromDateTime(scope.row.create_time) }}</span>
                    </template>
                </el-table-column>

                <el-table-column label="Visibility" width="150">
                    <template #default="scope">
                        <el-tag v-if="scope.row.public" type="success" effect="light" round>Public</el-tag>
                        <div v-else class="dept-tags">
                            <el-tag v-for="department in scope.row.departments" :key="department.name" type="info" effect="light" round size="small">
                                {{ department.name }}
                            </el-tag>
                        </div>
                    </template>
                </el-table-column>

                <el-table-column label="Actions" width="100" align="center" fixed="right">
                    <template #default="scope">
                        <el-button 
                            v-if="scope.row.author.uid == authStore.user.uid" 
                            @click="onShowDialog(scope.$index)"
                            type="danger" 
                            icon="Delete" 
                            circle 
                            plain
                            class="delete-btn"
                        />
                        <span v-else class="no-action">-</span>
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

.card-header {
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

.title-container {
    display: flex;
    align-items: center;
}

.unread-dot {
    width: 6px;
    height: 6px;
    background: #f43f5e;
    border-radius: 50%;
    margin-right: 10px;
    flex-shrink: 0;
    box-shadow: 0 0 8px rgba(244, 63, 94, 0.6);
}

.inform-link {
    text-decoration: none;
    color: #475569;
    font-size: 14px;
    transition: all 0.2s ease;
}

.inform-link:hover {
    color: #38bdf8;
}

.unread-title {
    font-weight: 600;
    color: #1e293b;
}

.publisher-info {
    display: flex;
    flex-direction: column;
    line-height: 1.4;
}

.dept-name {
    font-size: 11px;
    color: #94a3b8;
    text-transform: uppercase;
}

.author-name {
    font-size: 14px;
    font-weight: 500;
    color: #334155;
}

.time-text {
    font-size: 13px;
    color: #64748b;
}

.dept-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
}

.delete-btn {
    transition: transform 0.2s;
}

.delete-btn:hover {
    transform: scale(1.1);
}

.no-action {
    color: #cbd5e1;
    font-size: 12px;
}

.confirm-content {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 10px 0;
}

.warning-icon {
    font-size: 24px;
    color: #f43f5e;
}

.pagination-wrapper {
    display: flex;
    justify-content: flex-end;
    padding: 10px 0;
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
    .header-text {
        font-size: 14px;
    }
}
</style>