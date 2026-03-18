<script setup name="staffadd">
import { ref, reactive, onMounted, computed } from 'vue';
import staffHttp from '@/api/staffHttp';
import { useRouter } from 'vue-router';
import OAMain from "@/components/OAMain.vue"
import {useAuthStore} from "@/stores/auth"
import { ElMessage } from 'element-plus';

const router = useRouter();
const authStore = useAuthStore()

let departments = ref([]);

// Only department leaders can add new staff to their department
let staffForm = reactive({
    email: "",
    password: "",
    realname: "",
    department_id: null
});
const formRef = ref()

const validatePwd = (rule, value, callback) => {
    const pwdRegex = /^[a-zA-Z0-9]{6,20}$/
    if (!pwdRegex.test(value)) {
        callback(new Error('Password must be 6-20 characters long and contain only letters and numbers.'))
    } else {
        callback()
    }
}

let rules = reactive({
    email: [{required: true, message: "Please enter email!", trigger: 'blur'}],
    password: [
        {required: true, message: "Please enter password!", trigger: 'blur'},
        {validator: validatePwd, trigger: 'blur'}
    ],
    realname: [{required: true, message: "Please enter real name!", trigger: 'blur'}],
    department_id: [{required: authStore.user.department.name === 'Board Department', message: "Please select a department!", trigger: 'change'}],
})

const currentLeader = computed(() => {
    if (authStore.user.department.name === 'Board Department') {
        if (!staffForm.department_id) return "";
        const dept = departments.value.find(d => d.id === staffForm.department_id);
        if (dept && dept.leader) {
            return '[' + dept.leader.email + '] ' + dept.leader.realname;
        }
        return "No leader currently assigned";
    }
    return '[' + authStore.user.email + '] ' + authStore.user.realname;
});

onMounted(async () => {
    if (authStore.user.department.name === 'Board Department') {
        try {
            let deptData = await staffHttp.getAllDepartment()
            departments.value = deptData.results || deptData
        } catch (detail) {
            ElMessage.error(detail)
        }
    }
})

const onSubmit = () => {
    formRef.value.validate(async (valid, fields) => {
        if(valid){
            try{
                await staffHttp.addStaff(staffForm.realname, staffForm.email, staffForm.password, staffForm.department_id)
                ElMessage.success('Staff added successfully!')
                router.push({name: 'staff_list'})
            }catch(detail){
                ElMessage.error(detail)
            }
        }
    })
}

</script>

<template>
    <OAMain title="Add Staff">
        <el-card shadow="always">
            <el-form :rules="rules" :model="staffForm" ref="formRef" label-width="80px">
                <el-form-item label="Name" prop="realname">
                    <el-input v-model="staffForm.realname" placeholder="Please enter name">
                    </el-input>
                </el-form-item>

                <el-form-item label="Email" prop="email">
                    <el-input v-model="staffForm.email" placeholder="Please enter email"> </el-input>
                </el-form-item>

                <el-form-item label="Password" prop="password">
                    <el-input v-model="staffForm.password" placeholder="Please enter password" type="password">
                    </el-input>
                </el-form-item>

                <el-form-item label="Department" prop="department_id">
                    <el-select 
                        v-if="authStore.user.department.name === 'Board Department'" 
                        v-model="staffForm.department_id" 
                        placeholder="Please select a department"
                        style="width: 100%"
                    >
                        <el-option 
                            v-for="dept in departments" 
                            :key="dept.id" 
                            :label="dept.name" 
                            :value="dept.id" 
                        />
                    </el-select>
                    <el-input 
                        v-else 
                        readonly 
                        disabled 
                        placeholder="Please enter department" 
                        :value="authStore.user.department.name">
                    </el-input>
                </el-form-item>

                <el-form-item label="Leader">
                    <el-input 
                        readonly 
                        disabled 
                        placeholder="The leader will be displayed automatically"
                        :value="currentLeader"
                    >
                    </el-input>
                </el-form-item>

                <el-form-item>
                    <el-button type="primary" @click="onSubmit"> Submit </el-button>
                </el-form-item>
            </el-form>
        </el-card>
    </OAMain>
</template>

<style scoped></style>