package com.accounting.app.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.accounting.app.api.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class AccountViewModel : ViewModel() {
    private val _accounts = MutableStateFlow<List<Account>>(emptyList())
    val accounts: StateFlow<List<Account>> = _accounts

    private val _loading = MutableStateFlow(false)
    val loading: StateFlow<Boolean> = _loading

    private val _message = MutableStateFlow("")
    val message: StateFlow<String> = _message

    fun loadAccounts() {
        viewModelScope.launch {
            _loading.value = true
            try {
                val res = ApiClient.api.listAccounts()
                _accounts.value = res.data ?: emptyList()
            } catch (e: Exception) {
                _message.value = e.message ?: "加载失败"
            } finally {
                _loading.value = false
            }
        }
    }

    fun createAccount(name: String, type: Int, initialBalance: Double) {
        viewModelScope.launch {
            try {
                ApiClient.api.createAccount(AccountCreate(name, type, initial_balance = initialBalance))
                loadAccounts()
                _message.value = "添加成功"
            } catch (e: Exception) {
                _message.value = e.message ?: "添加失败"
            }
        }
    }

    fun deleteAccount(id: Int) {
        viewModelScope.launch {
            try {
                ApiClient.api.deleteAccount(id)
                loadAccounts()
                _message.value = "删除成功"
            } catch (e: Exception) {
                _message.value = e.message ?: "删除失败"
            }
        }
    }
}
