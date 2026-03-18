import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

const USER_KEY = "OA_USER_KEY"
const TOKEN_KEY = "OA_TOKEN_KEY"

export const PermissionChoices = {
  // All permissions
  All: 0b111,
  // Regular employee permissions
  Staff: 0b000,
  // Requires board member permissions
  Boarder: 0b001,
  // TeamLeader permissions
  Leader: 0b010,
}

export const useAuthStore = defineStore('auth', () => {
  let _user = ref({})
  let _token = ref("")

  function setUserToken(user, token){
    // Save to object (in memory)
    _user.value = user;
    _token.value = token;

    // Store in browser's localStorage (on disk)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    localStorage.setItem(TOKEN_KEY, token);
  }

  function clearUserToken(){
    _user.value = {}
    _token.value = ""
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem(TOKEN_KEY)
  }

  // Computed property
  let user = computed(() => {
    // _user.value = {}
    // 
    // Empty object {}: if check returns true, Object.keys(_user.value).length==0
    // Empty string "": if check returns false
    if(Object.keys(_user.value) == 0){
      let user_str = localStorage.getItem(USER_KEY)
      if(user_str){
        _user.value = JSON.parse(user_str)
      }
    }
    return _user.value
  })

  let token = computed(() => {
    if(!_token.value){
      let token_str = localStorage.getItem(TOKEN_KEY)
      if(token_str){
        _token.value = token_str
      }
    }
    return _token.value;
  })

  let is_logined = computed(() => {
    if(Object.keys(user.value).length>0 && token.value){
      return true;
    }
    return false;
  })

  let own_permissions = computed(() => {
    // 0b000
    let _permissions = PermissionChoices.Staff
    if(is_logined.value){
      // Check if user is a board member
      if(user.value.department.name == 'Board Department'){
        // 0b000 | 0b001 = 0b001
        _permissions |= PermissionChoices.Boarder
      }

      // Check if user is a team leader
      if(user.value.department?.leader?.uid == user.value.uid || user.value.department?.manager == user.value.uid){
        _permissions |= PermissionChoices.Leader
      }
    }
    return _permissions
  })

  function has_permission(permissions, opt='|'){
    // opt optional values:
    // 1. |: OR operation
    // 2. &: AND operation
    // own_permissions: 0b001
    // permissions: [0b010, 0b001]
    let results = permissions.map((permission) => (permission&own_permissions.value)==permission)
    // results = [true, false, false, true]
    if(opt == "|"){
      if(results.indexOf(true) >= 0){
        return true;
      }else{
        return false;
      }
    }else{
      if(results.indexOf(false) >= 0){
        return false;
      }else{
        return true
      }
    }
  }

  // 
  return { setUserToken, user, token, is_logined, clearUserToken, has_permission }
})