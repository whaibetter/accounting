package com.accounting.app.viewmodel

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.accounting.app.api.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.net.ConnectException
import java.net.SocketTimeoutException
import java.net.UnknownHostException

class AuthViewModel : ViewModel() {
    private val _isAuthenticated = MutableStateFlow(false)
    val isAuthenticated: StateFlow<Boolean> = _isAuthenticated

    private val _loading = MutableStateFlow(false)
    val loading: StateFlow<Boolean> = _loading

    private val _error = MutableStateFlow("")
    val error: StateFlow<String> = _error

    init {
        viewModelScope.launch {
            val token = ApiClient.getToken()
            if (token.isNotEmpty()) {
                _isAuthenticated.value = true
            }
        }
    }

    fun login(password: String) {
        if (password.isBlank()) {
            _error.value = "请输入密码"
            return
        }
        
        viewModelScope.launch {
            _loading.value = true
            _error.value = ""
            try {
                val response = ApiClient.api.login(LoginRequest(password))
                if (response.code == 200) {
                    val token = response.data?.access_token
                    if (!token.isNullOrBlank()) {
                        ApiClient.saveToken(token)
                        _isAuthenticated.value = true
                    } else {
                        _error.value = "登录失败：服务器返回数据异常"
                    }
                } else {
                    _error.value = "登录失败：${response.message.ifBlank { "密码错误或服务器错误" }}"
                }
            } catch (e: SocketTimeoutException) {
                _error.value = "网络超时，请检查网络连接后重试"
                Log.e("AuthViewModel", "Login timeout", e)
            } catch (e: UnknownHostException) {
                _error.value = "无法连接到服务器，请检查网络"
                Log.e("AuthViewModel", "Unknown host", e)
            } catch (e: ConnectException) {
                _error.value = "服务器连接失败，请稍后重试"
                Log.e("AuthViewModel", "Connection failed", e)
            } catch (e: Exception) {
                _error.value = "登录失败：${e.message ?: "未知错误"}"
                Log.e("AuthViewModel", "Login error", e)
            } finally {
                _loading.value = false
            }
        }
    }

    fun logout() {
        viewModelScope.launch {
            try {
                ApiClient.clearToken()
            } catch (e: Exception) {
                Log.e("AuthViewModel", "Logout error", e)
            }
            _isAuthenticated.value = false
        }
    }

    fun clearError() {
        _error.value = ""
    }
}
