package com.accounting.app.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.accounting.app.api.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class DataViewModel : ViewModel() {
    private val _accounts = MutableStateFlow<List<Account>>(emptyList())
    val accounts: StateFlow<List<Account>> = _accounts

    private val _expenseCategories = MutableStateFlow<List<Category>>(emptyList())
    val expenseCategories: StateFlow<List<Category>> = _expenseCategories

    private val _incomeCategories = MutableStateFlow<List<Category>>(emptyList())
    val incomeCategories: StateFlow<List<Category>> = _incomeCategories

    private val _tags = MutableStateFlow<List<Tag>>(emptyList())
    val tags: StateFlow<List<Tag>> = _tags

    private val _loaded = MutableStateFlow(false)
    val loaded: StateFlow<Boolean> = _loaded

    private val _loading = MutableStateFlow(false)
    val loading: StateFlow<Boolean> = _loading

    fun loadAll() {
        if (_loaded.value) return
        viewModelScope.launch {
            _loading.value = true
            try {
                val accRes = ApiClient.api.listAccounts()
                val expRes = ApiClient.api.listCategories(1)
                val incRes = ApiClient.api.listCategories(2)
                val tagRes = ApiClient.api.listTags()
                _accounts.value = accRes.data ?: emptyList()
                _expenseCategories.value = expRes.data ?: emptyList()
                _incomeCategories.value = incRes.data ?: emptyList()
                _tags.value = tagRes.data ?: emptyList()
                _loaded.value = true
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                _loading.value = false
            }
        }
    }

    fun refreshAccounts() {
        viewModelScope.launch {
            try {
                val res = ApiClient.api.listAccounts()
                _accounts.value = res.data ?: emptyList()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun refreshTags() {
        viewModelScope.launch {
            try {
                val res = ApiClient.api.listTags()
                _tags.value = res.data ?: emptyList()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun forceReload() {
        _loaded.value = false
        loadAll()
    }
}
