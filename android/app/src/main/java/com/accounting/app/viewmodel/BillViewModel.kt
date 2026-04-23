package com.accounting.app.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.accounting.app.api.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class BillViewModel : ViewModel() {
    private val _bills = MutableStateFlow<List<Bill>>(emptyList())
    val bills: StateFlow<List<Bill>> = _bills

    private val _loading = MutableStateFlow(false)
    val loading: StateFlow<Boolean> = _loading

    private val _total = MutableStateFlow(0)
    val total: StateFlow<Int> = _total

    fun loadBills(
        page: Int = 1,
        size: Int = 100,
        startDate: String? = null,
        endDate: String? = null,
        type: Int? = null
    ) {
        viewModelScope.launch {
            _loading.value = true
            try {
                val res = ApiClient.api.listBills(page, size, startDate, endDate, type)
                _bills.value = res.data?.items ?: emptyList()
                _total.value = res.data?.total ?: 0
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                _loading.value = false
            }
        }
    }

    fun createBill(bill: BillCreate, onSuccess: () -> Unit = {}, onError: (String) -> Unit = {}) {
        viewModelScope.launch {
            try {
                ApiClient.api.createBill(bill)
                onSuccess()
            } catch (e: Exception) {
                onError(e.message ?: "保存失败")
            }
        }
    }

    fun updateBill(id: Int, bill: BillUpdate, onSuccess: () -> Unit = {}, onError: (String) -> Unit = {}) {
        viewModelScope.launch {
            try {
                ApiClient.api.updateBill(id, bill)
                onSuccess()
            } catch (e: Exception) {
                onError(e.message ?: "更新失败")
            }
        }
    }

    fun deleteBill(id: Int, onSuccess: () -> Unit = {}, onError: (String) -> Unit = {}) {
        viewModelScope.launch {
            try {
                ApiClient.api.deleteBill(id)
                onSuccess()
            } catch (e: Exception) {
                onError(e.message ?: "删除失败")
            }
        }
    }
}
