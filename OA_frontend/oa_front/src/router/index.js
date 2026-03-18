import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import frame_routes from "@/router/frame"
import login_routes from "@/router/login"

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: frame_routes.concat(login_routes)
})

router.beforeEach((to, from) => {
  // Check if user is logged in, if not logged in
  // and the visited page is not the login page, redirect to login page
  const authStore = useAuthStore()
  if(!authStore.is_logined && to.name != 'login'){
    return {name: 'login'}
  }
})


export default router





