package com.accounting.app.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.accounting.app.api.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class StatsViewModel : ViewModel() {
    private val _overview = MutableStateFlow<Overview?>(null)
    val overview: StateFlow<Overview?> = _overview

    private val _categoryStats = MutableStateFlow<List<CategoryStat>>(emptyList())
    val categoryStats: StateFlow<List<CategoryStat>> = _categoryStats

    private val _trendData = MutableStateFlow<List<TrendItem>>(emptyList())
    val trendData: StateFlow<List<TrendItem>> = _trendData

    private val _loading = MutableStateFlow(false)
    val loading: StateFlow<Boolean> = _loading

    fun loadStats(startDate: String, endDate: String) {
        viewModelScope.launch {
            _loading.value = true
            try {
                val overviewRes = ApiClient.api.getOverview(startDate, endDate)
                _overview.value = overviewRes.data

                val statsRes = ApiClient.api.getCategoryStats(startDate, endDate, 1)
                _categoryStats.value = statsRes.data ?: emptyList()

                val trendRes = ApiClient.api.getTrend(startDate, endDate, "day")
                _trendData.value = trendRes.data ?: emptyList()
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                _loading.value = false
            }
        }
    }
}
