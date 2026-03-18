<script setup name="home">
import { ref, reactive, onMounted } from "vue"
import { ElMessage } from "element-plus"
import timeFormatter from "@/utils/timeFormatter";
import OAMain from "@/components/OAMain.vue"
import homeHttp from "@/api/homeHttp";
import * as echarts from 'echarts';

let informs = ref([])
let absents = ref([])

onMounted(async () => {
    try {
        informs.value = await homeHttp.getLatestInforms()
        absents.value = await homeHttp.getLatestAbsents()

        let rows = await homeHttp.getDepartmentStaffCount()
        console.log(rows);
        let xdatas = []
        let ydatas = []
        for (let row of rows) {
            xdatas.push(row.name)
            ydatas.push(row.staff_count)
        }

        // Based on prepared dom, initialize echarts instance
        var myChart = echarts.init(document.getElementById('department-staff-count'));
        // Draw chart
        myChart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                borderRadius: 8,
                borderWidth: 0,
                shadowBlur: 10,
                shadowColor: 'rgba(0,0,0,0.1)'
            },
            grid: {
                left: '3%',
                right: '3%',
                bottom: '10%',
                top: '15%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: xdatas,
                axisLine: { lineStyle: { color: '#e2e8f0' } },
                axisLabel: {
                    interval: 0,
                    width: 90,
                    overflow: 'break',
                    color: '#64748b',
                    fontSize: 12
                },
                axisTick: { show: false }
            },
            yAxis: {
                type: 'value',
                axisLine: { show: false },
                splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } },
                axisLabel: { color: '#94a3b8' }
            },
            series: [
                {
                    name: 'Staff Count',
                    type: 'bar',
                    barWidth: '40%',
                    itemStyle: {
                        borderRadius: [6, 6, 0, 0],
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: '#38bdf8' },
                            { offset: 1, color: '#818cf8' }
                        ])
                    },
                    emphasis: {
                        itemStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: '#7dd3fc' },
                                { offset: 1, color: '#a5b4fc' }
                            ])
                        }
                    },
                    data: ydatas
                }
            ]
        });

        window.addEventListener('resize', () => myChart.resize());
    } catch (detail) {
        ElMessage.error(detail)
    }
})

</script>

<template>
    <OAMain title="Home">
        <el-card class="chart-card">
            <template #header>
                <div class="card-header">
                    <span class="header-dot"></span>
                    <span class="header-text">Department Staff Count</span>
                </div>
            </template>
            <div id="department-staff-count" style="width: 100%;height:320px;"></div>
        </el-card>

        <el-row :gutter="24">
            <el-col :xs="24" :sm="12" style="margin-bottom: 24px;">
                <el-card class="table-card" shadow="hover">
                    <template #header>
                        <div class="card-header">
                            <span class="header-dot" style="background: #f43f5e;"></span>
                            <span class="header-text">Latest Notifications</span>
                        </div>
                    </template>
                    <el-table :data="informs" class="custom-table">
                        <el-table-column label="Title" min-width="150">
                            <template #default="scope">
                                <router-link class="link-text" :to="{ name: 'inform_detail', params: { pk: scope.row.id } }">
                                    {{ scope.row.title }}
                                </router-link>
                            </template>
                        </el-table-column>
                        <el-table-column label="Publisher" prop="author.realname" width="100"></el-table-column>
                        <el-table-column label="Time" width="120">
                            <template #default="scope">
                                <span class="time-text">{{ timeFormatter.stringFromDate(scope.row.create_time) }}</span>
                            </template>
                        </el-table-column>
                        <el-table-column label="Status" width="100" align="center">
                            <template #default="scope">
                                <el-tag v-if="scope.row.reads.length > 0" size="small" effect="light" round>Read</el-tag>
                                <el-tag v-else type="danger" size="small" effect="light" round>Unread</el-tag>
                            </template>
                        </el-table-column>
                    </el-table>
                </el-card>
            </el-col>
            
            <el-col :xs="24" :sm="12" style="margin-bottom: 24px;">
                <el-card class="table-card" shadow="hover">
                    <template #header>
                        <div class="card-header">
                            <span class="header-dot" style="background: #10b981;"></span>
                            <span class="header-text">Latest Leave Requests</span>
                        </div>
                    </template>
                    <el-table :data="absents" class="custom-table">
                        <el-table-column label="Requester" width="100">
                             <template #default="scope">
                                <span style="font-weight: 500;">{{ scope.row.requester.realname }}</span>
                            </template>
                        </el-table-column>
                        <el-table-column label="Department" prop="requester.department.name"></el-table-column>
                        <el-table-column label="Duration" min-width="180">
                            <template #default="scope">
                                <div class="duration-text">
                                    {{ scope.row.start_date }} <span style="color: #cbd5e1;">➔</span> {{ scope.row.end_date }}
                                </div>
                            </template>
                        </el-table-column>
                    </el-table>
                </el-card>
            </el-col>
        </el-row>
    </OAMain>
</template>

<style scoped>
.chart-card {
    margin-bottom: 24px;
    border: none;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(12px);
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
}

.table-card {
    border: none;
    border-radius: 16px;
    background: #ffffff;
    transition: transform 0.3s ease;
}

.card-header {
    display: flex;
    align-items: center;
}

.header-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #38bdf8;
    margin-right: 10px;
}

.header-text {
    font-size: 16px;
    font-weight: 600;
    color: #1e293b;
}

.link-text {
    color: #38bdf8;
    text-decoration: none;
    font-weight: 500;
}

.link-text:hover {
    color: #0ea5e9;
    text-decoration: underline;
}

.time-text, .duration-text {
    font-size: 13px;
    color: #64748b;
}

:deep(.el-card__header) {
    border-bottom: 1px solid #f1f5f9;
    padding: 18px 20px;
}

:deep(.el-table) {
    --el-table-border-color: #f1f5f9;
    --el-table-header-bg-color: #f8fafc;
}

:deep(.el-table th.el-table__cell) {
    font-weight: 600;
    color: #475569;
}
</style>