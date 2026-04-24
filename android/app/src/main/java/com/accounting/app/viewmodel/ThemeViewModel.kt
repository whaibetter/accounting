package com.accounting.app.viewmodel

import android.app.Application
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

val Application.themeDataStore: DataStore<Preferences> by preferencesDataStore(name = "theme_prefs")

enum class ThemeMode {
    SYSTEM, DARK, LIGHT
}

class ThemeViewModel(application: Application) : AndroidViewModel(application) {
    private val THEME_KEY = stringPreferencesKey("theme_mode")

    private val _themeMode = MutableStateFlow(ThemeMode.SYSTEM)
    val themeMode: StateFlow<ThemeMode> = _themeMode

    init {
        viewModelScope.launch {
            val saved = getApplication<Application>().themeDataStore.data.map {
                val str = it[THEME_KEY] ?: "SYSTEM"
                try { ThemeMode.valueOf(str) } catch (_: Exception) { ThemeMode.SYSTEM }
            }.first()
            _themeMode.value = saved
        }
    }

    fun setThemeMode(mode: ThemeMode) {
        _themeMode.value = mode
        viewModelScope.launch {
            getApplication<Application>().themeDataStore.edit { it[THEME_KEY] = mode.name }
        }
    }
}
